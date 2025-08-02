package mcp

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
)

type PortfolioService interface {
	GetHoldings(ctx context.Context, params GetHoldingsParams) (*MCPToolCallResponse, error)
	AddHolding(ctx context.Context, params AddHoldingParams) (*MCPToolCallResponse, error)
	UpdateHolding(ctx context.Context, params UpdateHoldingParams) (*MCPToolCallResponse, error)
	DeleteHolding(ctx context.Context, params DeleteHoldingParams) (*MCPToolCallResponse, error)
	GetPortfolioSummary(ctx context.Context, params GetPortfolioSummaryParams) (*MCPToolCallResponse, error)
	RebalanceHoldings(ctx context.Context, params RebalanceHoldingsParams) (*MCPToolCallResponse, error)
	ResetPortfolio(ctx context.Context, params ResetPortfolioParams) (*MCPToolCallResponse, error)
	SetTargetPortfolio(ctx context.Context, params SetTargetPortfolioParams) (*MCPToolCallResponse, error)
}

type Handler struct {
	portfolioService PortfolioService
}

func NewHandler(portfolioService PortfolioService) *Handler {
	return &Handler{
		portfolioService: portfolioService,
	}
}

func (h *Handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	w.Header().Set("Content-Type", "application/json")

	var req JSONRPCRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		h.sendError(w, nil, -32700, "Parse error", err.Error())
		return
	}

	// Validate JSON-RPC version
	if req.JSONRPC != "2.0" {
		h.sendError(w, req.ID, -32600, "Invalid Request", "jsonrpc must be '2.0'")
		return
	}

	ctx := r.Context()

	switch req.Method {
	case "initialize":
		h.handleInitialize(w, req)
	case "notifications/initialized":
		h.handleNotificationsInitialized(w, req)
	case "ping":
		h.handlePing(w, req)
	case "tools/list":
		h.handleToolsList(w, req)
	case "tools/call":
		h.handleToolsCall(w, req, ctx)
	default:
		h.sendError(w, req.ID, -32601, "Method not found", fmt.Sprintf("Unknown method: %s", req.Method))
	}
}

func (h *Handler) handleInitialize(w http.ResponseWriter, req JSONRPCRequest) {
	response := JSONRPCResponse{
		JSONRPC: "2.0",
		ID:      req.ID,
		Result: map[string]interface{}{
			"protocolVersion": "2024-11-05",
			"capabilities": map[string]interface{}{
				"tools": map[string]interface{}{
					"listChanged": false,
				},
			},
			"serverInfo": map[string]interface{}{
				"name":    "portfolio-db",
				"version": "1.0.0",
			},
		},
	}
	json.NewEncoder(w).Encode(response)
}

func (h *Handler) handleNotificationsInitialized(w http.ResponseWriter, req JSONRPCRequest) {
	// Always send a valid JSON response for MCP client compatibility
	// Use a default ID of 0 if the notification has null/missing ID
	responseID := req.ID
	if responseID == nil {
		responseID = 0
	}

	response := JSONRPCResponse{
		JSONRPC: "2.0",
		ID:      responseID,
		Result:  map[string]interface{}{},
	}
	json.NewEncoder(w).Encode(response)
}

func (h *Handler) handlePing(w http.ResponseWriter, req JSONRPCRequest) {
	response := JSONRPCResponse{
		JSONRPC: "2.0",
		ID:      req.ID,
		Result:  map[string]interface{}{},
	}
	json.NewEncoder(w).Encode(response)
}

func (h *Handler) handleToolsList(w http.ResponseWriter, req JSONRPCRequest) {
	tools := []MCPTool{
		{
			Name:        "get_holdings",
			Description: "Get all current portfolio holdings",
			InputSchema: GetHoldingsSchema,
		},
		{
			Name:        "add_holding",
			Description: "Add a new holding to the portfolio",
			InputSchema: AddHoldingSchema,
		},
		{
			Name:        "update_holding",
			Description: "Update an existing portfolio holding",
			InputSchema: UpdateHoldingSchema,
		},
		{
			Name:        "delete_holding",
			Description: "Delete a holding from the portfolio",
			InputSchema: DeleteHoldingSchema,
		},
		{
			Name:        "get_portfolio_summary",
			Description: "Get portfolio summary statistics",
			InputSchema: GetPortfolioSummarySchema,
		},
		{
			Name:        "rebalance_holdings",
			Description: "Rebalance portfolio holdings to new weights",
			InputSchema: RebalanceHoldingsSchema,
		},
		{
			Name:        "reset_portfolio",
			Description: "Reset the entire portfolio by removing all holdings",
			InputSchema: ResetPortfolioSchema,
		},
		{
			Name:        "set_target_portfolio",
			Description: "Set the entire portfolio to specified target holdings",
			InputSchema: SetTargetPortfolioSchema,
		},
	}

	response := JSONRPCResponse{
		JSONRPC: "2.0",
		ID:      req.ID,
		Result:  MCPToolsListResponse{Tools: tools},
	}

	json.NewEncoder(w).Encode(response)
}

func (h *Handler) handleToolsCall(w http.ResponseWriter, req JSONRPCRequest, ctx context.Context) {
	// Parse the tools/call parameters
	var toolCallReq MCPToolsCallRequest
	if err := json.Unmarshal([]byte(fmt.Sprintf(`{
		"jsonrpc": "%s",
		"id": %v,
		"method": "%s",
		"params": %s
	}`, req.JSONRPC, req.ID, req.Method, mustMarshal(req.Params))), &toolCallReq); err != nil {
		h.sendError(w, req.ID, -32602, "Invalid params", err.Error())
		return
	}

	var result *MCPToolCallResponse
	var err error

	switch toolCallReq.Params.Name {
	case "get_holdings":
		var params GetHoldingsParams
		result, err = h.portfolioService.GetHoldings(ctx, params)

	case "add_holding":
		var params AddHoldingParams
		if err := mapToStruct(toolCallReq.Params.Arguments, &params); err != nil {
			h.sendError(w, req.ID, -32602, "Invalid params", err.Error())
			return
		}
		result, err = h.portfolioService.AddHolding(ctx, params)

	case "update_holding":
		var params UpdateHoldingParams
		if err := mapToStruct(toolCallReq.Params.Arguments, &params); err != nil {
			h.sendError(w, req.ID, -32602, "Invalid params", err.Error())
			return
		}
		result, err = h.portfolioService.UpdateHolding(ctx, params)

	case "delete_holding":
		var params DeleteHoldingParams
		if err := mapToStruct(toolCallReq.Params.Arguments, &params); err != nil {
			h.sendError(w, req.ID, -32602, "Invalid params", err.Error())
			return
		}
		result, err = h.portfolioService.DeleteHolding(ctx, params)

	case "get_portfolio_summary":
		var params GetPortfolioSummaryParams
		result, err = h.portfolioService.GetPortfolioSummary(ctx, params)

	case "rebalance_holdings":
		var params RebalanceHoldingsParams
		if err := mapToStruct(toolCallReq.Params.Arguments, &params); err != nil {
			h.sendError(w, req.ID, -32602, "Invalid params", err.Error())
			return
		}
		result, err = h.portfolioService.RebalanceHoldings(ctx, params)

	case "reset_portfolio":
		var params ResetPortfolioParams
		if err := mapToStruct(toolCallReq.Params.Arguments, &params); err != nil {
			h.sendError(w, req.ID, -32602, "Invalid params", err.Error())
			return
		}
		result, err = h.portfolioService.ResetPortfolio(ctx, params)

	case "set_target_portfolio":
		var params SetTargetPortfolioParams
		if err := mapToStruct(toolCallReq.Params.Arguments, &params); err != nil {
			h.sendError(w, req.ID, -32602, "Invalid params", err.Error())
			return
		}
		result, err = h.portfolioService.SetTargetPortfolio(ctx, params)

	default:
		h.sendError(w, req.ID, -32601, "Method not found", fmt.Sprintf("Unknown tool: %s", toolCallReq.Params.Name))
		return
	}

	if err != nil {
		h.sendError(w, req.ID, -32603, "Internal error", err.Error())
		return
	}

	response := JSONRPCResponse{
		JSONRPC: "2.0",
		ID:      req.ID,
		Result:  result,
	}

	json.NewEncoder(w).Encode(response)
}

func (h *Handler) sendError(w http.ResponseWriter, id interface{}, code int, message, data string) {
	response := JSONRPCResponse{
		JSONRPC: "2.0",
		ID:      id,
		Error: &JSONRPCError{
			Code:    code,
			Message: message,
			Data:    data,
		},
	}
	w.WriteHeader(http.StatusOK) // JSON-RPC errors are still HTTP 200
	json.NewEncoder(w).Encode(response)
}

// Helper function to convert map to struct
func mapToStruct(m map[string]interface{}, result interface{}) error {
	jsonBytes, err := json.Marshal(m)
	if err != nil {
		return err
	}
	return json.Unmarshal(jsonBytes, result)
}

// Helper function to marshal to JSON
func mustMarshal(v interface{}) string {
	b, err := json.Marshal(v)
	if err != nil {
		return "{}"
	}
	return string(b)
}
