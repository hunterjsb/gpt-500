package mcp

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
)

type HeadlinesService interface {
	GetGeneralHeadlines(ctx context.Context, params GetGeneralHeadlinesParams) (*MCPToolCallResponse, error)
	GetStockHeadlines(ctx context.Context, params GetStockHeadlinesParams) (*MCPToolCallResponse, error)
	GetSectorHeadlines(ctx context.Context, params GetSectorHeadlinesParams) (*MCPToolCallResponse, error)
	GetIndexHeadlines(ctx context.Context, params GetIndexHeadlinesParams) (*MCPToolCallResponse, error)
}

type Handler struct {
	headlinesService HeadlinesService
}

func NewHandler(headlinesService HeadlinesService) *Handler {
	return &Handler{
		headlinesService: headlinesService,
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
				"name":    "financial-headlines",
				"version": "1.0.0",
			},
		},
	}
	json.NewEncoder(w).Encode(response)
}

func (h *Handler) handleNotificationsInitialized(w http.ResponseWriter, req JSONRPCRequest) {
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
			Name:        "get_general_headlines",
			Description: "Get general financial market headlines",
			InputSchema: GetGeneralHeadlinesSchema,
		},
		{
			Name:        "get_stock_headlines",
			Description: "Get financial headlines for a specific stock ticker",
			InputSchema: GetStockHeadlinesSchema,
		},
		{
			Name:        "get_sector_headlines",
			Description: "Get financial headlines for a specific market sector",
			InputSchema: GetSectorHeadlinesSchema,
		},
		{
			Name:        "get_index_headlines",
			Description: "Get financial headlines for a specific market index",
			InputSchema: GetIndexHeadlinesSchema,
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
	case "get_general_headlines":
		var params GetGeneralHeadlinesParams
		result, err = h.headlinesService.GetGeneralHeadlines(ctx, params)

	case "get_stock_headlines":
		var params GetStockHeadlinesParams
		if err := mapToStruct(toolCallReq.Params.Arguments, &params); err != nil {
			h.sendError(w, req.ID, -32602, "Invalid params", err.Error())
			return
		}
		result, err = h.headlinesService.GetStockHeadlines(ctx, params)

	case "get_sector_headlines":
		var params GetSectorHeadlinesParams
		if err := mapToStruct(toolCallReq.Params.Arguments, &params); err != nil {
			h.sendError(w, req.ID, -32602, "Invalid params", err.Error())
			return
		}
		result, err = h.headlinesService.GetSectorHeadlines(ctx, params)

	case "get_index_headlines":
		var params GetIndexHeadlinesParams
		if err := mapToStruct(toolCallReq.Params.Arguments, &params); err != nil {
			h.sendError(w, req.ID, -32602, "Invalid params", err.Error())
			return
		}
		result, err = h.headlinesService.GetIndexHeadlines(ctx, params)

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
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}

func mapToStruct(m map[string]interface{}, result interface{}) error {
	jsonBytes, err := json.Marshal(m)
	if err != nil {
		return err
	}
	return json.Unmarshal(jsonBytes, result)
}

func mustMarshal(v interface{}) string {
	b, err := json.Marshal(v)
	if err != nil {
		return "{}"
	}
	return string(b)
}
