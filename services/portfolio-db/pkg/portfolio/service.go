package portfolio

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"strconv"

	"claude-20/services/portfolio-db/internal/db"
	"claude-20/services/portfolio-db/pkg/mcp"
)

type Service struct {
	queries  *db.Queries
	database *sql.DB
}

func NewService(database *sql.DB, queries *db.Queries) *Service {
	return &Service{
		queries:  queries,
		database: database,
	}
}

func (s *Service) GetHoldings(ctx context.Context, params mcp.GetHoldingsParams) (*mcp.Response, error) {
	holdings, err := s.queries.GetAllHoldings(ctx)
	if err != nil {
		return &mcp.Response{
			Content: []mcp.Content{{Type: "text", Text: fmt.Sprintf("Error querying holdings: %v", err)}},
			IsError: true,
		}, nil
	}

	holdingsJSON, _ := json.MarshalIndent(holdings, "", "  ")
	return &mcp.Response{
		Content: []mcp.Content{{Type: "text", Text: string(holdingsJSON)}},
	}, nil
}

func (s *Service) AddHolding(ctx context.Context, params mcp.AddHoldingParams) (*mcp.Response, error) {
	// Start transaction for smart rebalancing
	tx, err := s.database.BeginTx(ctx, nil)
	if err != nil {
		return &mcp.Response{
			Content: []mcp.Content{{Type: "text", Text: fmt.Sprintf("Error starting transaction: %v", err)}},
			IsError: true,
		}, nil
	}
	defer tx.Rollback()

	txQueries := s.queries.WithTx(tx)

	// Get current holdings to calculate rebalancing
	currentHoldings, err := txQueries.GetAllHoldings(ctx)
	if err != nil {
		return &mcp.Response{
			Content: []mcp.Content{{Type: "text", Text: fmt.Sprintf("Error getting current holdings: %v", err)}},
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
				return &mcp.Response{
					Content: []mcp.Content{{Type: "text", Text: fmt.Sprintf("Error rebalancing %s: %v", holding.Ticker, err)}},
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
		return &mcp.Response{
			Content: []mcp.Content{{Type: "text", Text: fmt.Sprintf("Error adding new holding: %v", err)}},
			IsError: true,
		}, nil
	}

	// Commit the transaction
	if err := tx.Commit(); err != nil {
		return &mcp.Response{
			Content: []mcp.Content{{Type: "text", Text: fmt.Sprintf("Error committing transaction: %v", err)}},
			IsError: true,
		}, nil
	}

	// Get final portfolio state
	finalHoldings, _ := s.queries.GetAllHoldings(ctx)
	finalJSON, _ := json.MarshalIndent(finalHoldings, "", "  ")

	return &mcp.Response{
		Content: []mcp.Content{{Type: "text", Text: fmt.Sprintf("Successfully added %s with automatic rebalancing:\n%s", params.Ticker, finalJSON)}},
	}, nil
}

func (s *Service) UpdateHolding(ctx context.Context, params mcp.UpdateHoldingParams) (*mcp.Response, error) {
	// First get the current holding to use as defaults
	current, err := s.queries.GetHolding(ctx, params.Ticker)
	if err != nil {
		return &mcp.Response{
			Content: []mcp.Content{{Type: "text", Text: fmt.Sprintf("Holding not found: %v", err)}},
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

	holding, err := s.queries.UpdateHolding(ctx, db.UpdateHoldingParams{
		Ticker:  params.Ticker,
		Name:    name,
		Weight:  weight,
		Price:   price,
		Comment: comment,
		Return:  returnVal,
	})

	if err != nil {
		return &mcp.Response{
			Content: []mcp.Content{{Type: "text", Text: fmt.Sprintf("Error updating holding: %v", err)}},
			IsError: true,
		}, nil
	}

	holdingJSON, _ := json.MarshalIndent(holding, "", "  ")
	return &mcp.Response{
		Content: []mcp.Content{{Type: "text", Text: fmt.Sprintf("Successfully updated %s:\n%s", params.Ticker, holdingJSON)}},
	}, nil
}

func (s *Service) DeleteHolding(ctx context.Context, params mcp.DeleteHoldingParams) (*mcp.Response, error) {
	err := s.queries.DeleteHolding(ctx, params.Ticker)
	if err != nil {
		return &mcp.Response{
			Content: []mcp.Content{{Type: "text", Text: fmt.Sprintf("Error deleting holding: %v", err)}},
			IsError: true,
		}, nil
	}

	return &mcp.Response{
		Content: []mcp.Content{{Type: "text", Text: fmt.Sprintf("Successfully deleted %s from portfolio", params.Ticker)}},
	}, nil
}

func (s *Service) GetPortfolioSummary(ctx context.Context, params mcp.GetPortfolioSummaryParams) (*mcp.Response, error) {
	summary, err := s.queries.GetPortfolioSummary(ctx)
	if err != nil {
		return &mcp.Response{
			Content: []mcp.Content{{Type: "text", Text: fmt.Sprintf("Error getting portfolio summary: %v", err)}},
			IsError: true,
		}, nil
	}

	summaryJSON, _ := json.MarshalIndent(summary, "", "  ")
	return &mcp.Response{
		Content: []mcp.Content{{Type: "text", Text: string(summaryJSON)}},
	}, nil
}

func (s *Service) RebalanceHoldings(ctx context.Context, params mcp.RebalanceHoldingsParams) (*mcp.Response, error) {
	// Start a transaction
	tx, err := s.database.BeginTx(ctx, nil)
	if err != nil {
		return &mcp.Response{
			Content: []mcp.Content{{Type: "text", Text: fmt.Sprintf("Error starting transaction: %v", err)}},
			IsError: true,
		}, nil
	}
	defer tx.Rollback()

	txQueries := s.queries.WithTx(tx)

	// Update all holdings in the transaction
	var updatedHoldings []db.PortfolioHolding
	for _, holding := range params.Holdings {
		// Get current holding to preserve other fields
		current, err := txQueries.GetHolding(ctx, holding.Ticker)
		if err != nil {
			return &mcp.Response{
				Content: []mcp.Content{{Type: "text", Text: fmt.Sprintf("Holding %s not found: %v", holding.Ticker, err)}},
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
			return &mcp.Response{
				Content: []mcp.Content{{Type: "text", Text: fmt.Sprintf("Error updating %s: %v", holding.Ticker, err)}},
				IsError: true,
			}, nil
		}

		updatedHoldings = append(updatedHoldings, updated)
	}

	// Commit the transaction
	if err := tx.Commit(); err != nil {
		return &mcp.Response{
			Content: []mcp.Content{{Type: "text", Text: fmt.Sprintf("Error committing transaction: %v", err)}},
			IsError: true,
		}, nil
	}

	resultJSON, _ := json.MarshalIndent(updatedHoldings, "", "  ")
	return &mcp.Response{
		Content: []mcp.Content{{Type: "text", Text: fmt.Sprintf("Successfully rebalanced holdings:\n%s", resultJSON)}},
	}, nil
}