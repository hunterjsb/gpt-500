package main

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"

	"claude-20/services/portfolio-db/internal/db"

	_ "github.com/lib/pq"
)

// MCP Tool request/response structures
type MCPRequest struct {
	Method string      `json:"method"`
	Params interface{} `json:"params"`
}

type MCPResponse struct {
	Content []MCPContent `json:"content"`
	IsError bool         `json:"isError,omitempty"`
}

type MCPContent struct {
	Type string `json:"type"`
	Text string `json:"text"`
}

type GetHoldingsParams struct{}

type AddHoldingParams struct {
	Ticker  string   `json:"ticker"`
	Name    string   `json:"name"`
	Weight  float64  `json:"weight"`
	Price   float64  `json:"price"`
	Comment *string  `json:"comment,omitempty"`
	Return  *float64 `json:"return,omitempty"`
}

type UpdateHoldingParams struct {
	Ticker  string   `json:"ticker"`
	Name    *string  `json:"name,omitempty"`
	Weight  *float64 `json:"weight,omitempty"`
	Price   *float64 `json:"price,omitempty"`
	Comment *string  `json:"comment,omitempty"`
	Return  *float64 `json:"return,omitempty"`
}

type DeleteHoldingParams struct {
	Ticker string `json:"ticker"`
}

type GetPortfolioSummaryParams struct{}

type RebalanceHoldingsParams struct {
	Holdings []struct {
		Ticker string  `json:"ticker"`
		Weight float64 `json:"weight"`
	} `json:"holdings"`
}

type RebalanceAndAddParams struct {
	UpdateHoldings []struct {
		Ticker string  `json:"ticker"`
		Weight float64 `json:"weight"`
	} `json:"update_holdings"`
	NewHoldings []struct {
		Ticker  string   `json:"ticker"`
		Name    string   `json:"name"`
		Weight  float64  `json:"weight"`
		Price   float64  `json:"price"`
		Comment *string  `json:"comment,omitempty"`
		Return  *float64 `json:"return,omitempty"`
	} `json:"new_holdings"`
}

// Database connection and queries
var database *sql.DB
var queries *db.Queries

func initDB() error {
	var err error
	// Use environment variables for database connection
	dbHost := getEnv("DB_HOST", "localhost")
	dbPort := getEnv("DB_PORT", "5432")
	dbUser := getEnv("DB_USER", "hunter")
	dbPassword := getEnv("DB_PASSWORD", "postgres")
	dbName := getEnv("DB_NAME", "gpt_500")

	connStr := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		dbHost, dbPort, dbUser, dbPassword, dbName)

	database, err = sql.Open("postgres", connStr)
	if err != nil {
		return err
	}

	if err = database.Ping(); err != nil {
		return err
	}

	queries = db.New(database)
	return nil
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

// MCP Tool implementations
func getHoldings(ctx context.Context, params GetHoldingsParams) (*MCPResponse, error) {
	holdings, err := queries.GetAllHoldings(ctx)
	if err != nil {
		return &MCPResponse{
			Content: []MCPContent{{Type: "text", Text: fmt.Sprintf("Error querying holdings: %v", err)}},
			IsError: true,
		}, nil
	}

	holdingsJSON, _ := json.MarshalIndent(holdings, "", "  ")
	return &MCPResponse{
		Content: []MCPContent{{Type: "text", Text: string(holdingsJSON)}},
	}, nil
}

func addHolding(ctx context.Context, params AddHoldingParams) (*MCPResponse, error) {
	// Start transaction for smart rebalancing
	tx, err := database.BeginTx(ctx, nil)
	if err != nil {
		return &MCPResponse{
			Content: []MCPContent{{Type: "text", Text: fmt.Sprintf("Error starting transaction: %v", err)}},
			IsError: true,
		}, nil
	}
	defer tx.Rollback()

	txQueries := queries.WithTx(tx)

	// Get current holdings to calculate rebalancing
	currentHoldings, err := txQueries.GetAllHoldings(ctx)
	if err != nil {
		return &MCPResponse{
			Content: []MCPContent{{Type: "text", Text: fmt.Sprintf("Error getting current holdings: %v", err)}},
			IsError: true,
		}, nil
	}

	// Calculate current total weight
	var currentTotal float64
	for _, holding := range currentHoldings {
		weight, _ := strconv.ParseFloat(holding.Weight, 64)
		currentTotal += weight
	}

	// If adding this holding would exceed 100%, proportionally reduce existing holdings
	newTotal := currentTotal + params.Weight
	if newTotal > 100.0 {
		// Calculate scale factor to make room
		availableForExisting := 100.0 - params.Weight
		scaleFactor := availableForExisting / currentTotal

		// Update all existing holdings proportionally
		for _, holding := range currentHoldings {
			currentWeight, _ := strconv.ParseFloat(holding.Weight, 64)
			newWeight := currentWeight * scaleFactor

			_, err := txQueries.UpdateHolding(ctx, db.UpdateHoldingParams{
				Ticker:  holding.Ticker,
				Name:    holding.Name,
				Weight:  fmt.Sprintf("%.3f", newWeight),
				Price:   holding.Price,
				Comment: holding.Comment,
				Return:  holding.Return,
			})

			if err != nil {
				return &MCPResponse{
					Content: []MCPContent{{Type: "text", Text: fmt.Sprintf("Error rebalancing %s: %v", holding.Ticker, err)}},
					IsError: true,
				}, nil
			}
		}
	}

	// Now add the new holding
	var comment sql.NullString
	if params.Comment != nil {
		comment = sql.NullString{String: *params.Comment, Valid: true}
	}

	var returnVal sql.NullString
	if params.Return != nil {
		returnVal = sql.NullString{String: fmt.Sprintf("%.4f", *params.Return), Valid: true}
	}

	_, err = txQueries.CreateHolding(ctx, db.CreateHoldingParams{
		Ticker:  params.Ticker,
		Name:    params.Name,
		Weight:  fmt.Sprintf("%.3f", params.Weight),
		Comment: comment,
		Price:   fmt.Sprintf("%.4f", params.Price),
		Return:  returnVal,
	})

	if err != nil {
		return &MCPResponse{
			Content: []MCPContent{{Type: "text", Text: fmt.Sprintf("Error adding new holding: %v", err)}},
			IsError: true,
		}, nil
	}

	// Commit the transaction
	if err := tx.Commit(); err != nil {
		return &MCPResponse{
			Content: []MCPContent{{Type: "text", Text: fmt.Sprintf("Error committing transaction: %v", err)}},
			IsError: true,
		}, nil
	}

	// Get final portfolio state
	finalHoldings, _ := queries.GetAllHoldings(ctx)
	finalJSON, _ := json.MarshalIndent(finalHoldings, "", "  ")

	return &MCPResponse{
		Content: []MCPContent{{Type: "text", Text: fmt.Sprintf("Successfully added %s with automatic rebalancing:\n%s", params.Ticker, finalJSON)}},
	}, nil
}

func updateHolding(ctx context.Context, params UpdateHoldingParams) (*MCPResponse, error) {
	// First get the current holding to use as defaults
	current, err := queries.GetHolding(ctx, params.Ticker)
	if err != nil {
		return &MCPResponse{
			Content: []MCPContent{{Type: "text", Text: fmt.Sprintf("Holding not found: %v", err)}},
			IsError: true,
		}, nil
	}

	// Use current values as defaults, override with provided params
	name := current.Name
	weight := current.Weight
	price := current.Price
	comment := current.Comment
	returnVal := current.Return

	if params.Name != nil {
		name = *params.Name
	}
	if params.Weight != nil {
		weight = fmt.Sprintf("%.3f", *params.Weight)
	}
	if params.Price != nil {
		price = fmt.Sprintf("%.4f", *params.Price)
	}
	if params.Comment != nil {
		comment = sql.NullString{String: *params.Comment, Valid: true}
	}
	if params.Return != nil {
		returnVal = sql.NullString{String: fmt.Sprintf("%.4f", *params.Return), Valid: true}
	}

	holding, err := queries.UpdateHolding(ctx, db.UpdateHoldingParams{
		Ticker:  params.Ticker,
		Name:    name,
		Weight:  weight,
		Price:   price,
		Comment: comment,
		Return:  returnVal,
	})

	if err != nil {
		return &MCPResponse{
			Content: []MCPContent{{Type: "text", Text: fmt.Sprintf("Error updating holding: %v", err)}},
			IsError: true,
		}, nil
	}

	holdingJSON, _ := json.MarshalIndent(holding, "", "  ")
	return &MCPResponse{
		Content: []MCPContent{{Type: "text", Text: fmt.Sprintf("Successfully updated %s:\n%s", params.Ticker, holdingJSON)}},
	}, nil
}

func deleteHolding(ctx context.Context, params DeleteHoldingParams) (*MCPResponse, error) {
	err := queries.DeleteHolding(ctx, params.Ticker)
	if err != nil {
		return &MCPResponse{
			Content: []MCPContent{{Type: "text", Text: fmt.Sprintf("Error deleting holding: %v", err)}},
			IsError: true,
		}, nil
	}

	return &MCPResponse{
		Content: []MCPContent{{Type: "text", Text: fmt.Sprintf("Successfully deleted %s from portfolio", params.Ticker)}},
	}, nil
}

func getPortfolioSummary(ctx context.Context, params GetPortfolioSummaryParams) (*MCPResponse, error) {
	summary, err := queries.GetPortfolioSummary(ctx)
	if err != nil {
		return &MCPResponse{
			Content: []MCPContent{{Type: "text", Text: fmt.Sprintf("Error getting portfolio summary: %v", err)}},
			IsError: true,
		}, nil
	}

	summaryJSON, _ := json.MarshalIndent(summary, "", "  ")
	return &MCPResponse{
		Content: []MCPContent{{Type: "text", Text: string(summaryJSON)}},
	}, nil
}

func rebalanceHoldings(ctx context.Context, params RebalanceHoldingsParams) (*MCPResponse, error) {
	// Start a transaction
	tx, err := database.BeginTx(ctx, nil)
	if err != nil {
		return &MCPResponse{
			Content: []MCPContent{{Type: "text", Text: fmt.Sprintf("Error starting transaction: %v", err)}},
			IsError: true,
		}, nil
	}
	defer tx.Rollback()

	txQueries := queries.WithTx(tx)

	// Update all holdings in the transaction
	var updatedHoldings []db.PortfolioHolding
	for _, holding := range params.Holdings {
		// Get current holding to preserve other fields
		current, err := txQueries.GetHolding(ctx, holding.Ticker)
		if err != nil {
			return &MCPResponse{
				Content: []MCPContent{{Type: "text", Text: fmt.Sprintf("Holding %s not found: %v", holding.Ticker, err)}},
				IsError: true,
			}, nil
		}

		updated, err := txQueries.UpdateHolding(ctx, db.UpdateHoldingParams{
			Ticker:  holding.Ticker,
			Name:    current.Name,
			Weight:  fmt.Sprintf("%.3f", holding.Weight),
			Price:   current.Price,
			Comment: current.Comment,
			Return:  current.Return,
		})

		if err != nil {
			return &MCPResponse{
				Content: []MCPContent{{Type: "text", Text: fmt.Sprintf("Error updating %s: %v", holding.Ticker, err)}},
				IsError: true,
			}, nil
		}

		updatedHoldings = append(updatedHoldings, updated)
	}

	// Commit the transaction
	if err := tx.Commit(); err != nil {
		return &MCPResponse{
			Content: []MCPContent{{Type: "text", Text: fmt.Sprintf("Error committing transaction: %v", err)}},
			IsError: true,
		}, nil
	}

	resultJSON, _ := json.MarshalIndent(updatedHoldings, "", "  ")
	return &MCPResponse{
		Content: []MCPContent{{Type: "text", Text: fmt.Sprintf("Successfully rebalanced holdings:\n%s", resultJSON)}},
	}, nil
}

// HTTP handler for MCP requests
func mcpHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	w.Header().Set("Content-Type", "application/json")

	var req MCPRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	ctx := r.Context()
	var response *MCPResponse
	var err error

	switch req.Method {
	case "get_holdings":
		var params GetHoldingsParams
		response, err = getHoldings(ctx, params)

	case "add_holding":
		var params AddHoldingParams
		if paramsBytes, marshalErr := json.Marshal(req.Params); marshalErr == nil {
			json.Unmarshal(paramsBytes, &params)
		}
		response, err = addHolding(ctx, params)

	case "update_holding":
		var params UpdateHoldingParams
		if paramsBytes, marshalErr := json.Marshal(req.Params); marshalErr == nil {
			json.Unmarshal(paramsBytes, &params)
		}
		response, err = updateHolding(ctx, params)

	case "delete_holding":
		var params DeleteHoldingParams
		if paramsBytes, marshalErr := json.Marshal(req.Params); marshalErr == nil {
			json.Unmarshal(paramsBytes, &params)
		}
		response, err = deleteHolding(ctx, params)

	case "get_portfolio_summary":
		var params GetPortfolioSummaryParams
		response, err = getPortfolioSummary(ctx, params)

	case "rebalance_holdings":
		var params RebalanceHoldingsParams
		if paramsBytes, marshalErr := json.Marshal(req.Params); marshalErr == nil {
			json.Unmarshal(paramsBytes, &params)
		}
		response, err = rebalanceHoldings(ctx, params)

	default:
		response = &MCPResponse{
			Content: []MCPContent{{Type: "text", Text: fmt.Sprintf("Unknown method: %s", req.Method)}},
			IsError: true,
		}
	}

	if err != nil {
		response = &MCPResponse{
			Content: []MCPContent{{Type: "text", Text: fmt.Sprintf("Internal error: %v", err)}},
			IsError: true,
		}
	}

	json.NewEncoder(w).Encode(response)
}

// Health check endpoint
func healthHandler(w http.ResponseWriter, r *http.Request) {
	if err := database.Ping(); err != nil {
		http.Error(w, "Database connection failed", http.StatusServiceUnavailable)
		return
	}
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("OK"))
}

func main() {
	if err := initDB(); err != nil {
		log.Fatal("Failed to connect to database:", err)
	}
	defer database.Close()

	http.HandleFunc("/mcp", mcpHandler)
	http.HandleFunc("/health", healthHandler)

	port := getEnv("PORT", "8080")
	log.Printf("Starting MCP server on port %s", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}
