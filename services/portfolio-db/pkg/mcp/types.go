package mcp

import "encoding/json"

// Standard JSON-RPC 2.0 types
type JSONRPCRequest struct {
	JSONRPC string      `json:"jsonrpc"`
	ID      interface{} `json:"id"`
	Method  string      `json:"method"`
	Params  interface{} `json:"params,omitempty"`
}

type JSONRPCResponse struct {
	JSONRPC string        `json:"jsonrpc"`
	ID      interface{}   `json:"id"`
	Result  interface{}   `json:"result,omitempty"`
	Error   *JSONRPCError `json:"error,omitempty"`
}

type JSONRPCError struct {
	Code    int         `json:"code"`
	Message string      `json:"message"`
	Data    interface{} `json:"data,omitempty"`
}

// MCP Protocol types
type MCPToolsListRequest struct {
	JSONRPC string      `json:"jsonrpc"`
	ID      interface{} `json:"id"`
	Method  string      `json:"method"` // Should be "tools/list"
}

type MCPToolsCallRequest struct {
	JSONRPC string            `json:"jsonrpc"`
	ID      interface{}       `json:"id"`
	Method  string            `json:"method"` // Should be "tools/call"
	Params  MCPToolCallParams `json:"params"`
}

type MCPToolCallParams struct {
	Name      string                 `json:"name"`
	Arguments map[string]interface{} `json:"arguments,omitempty"`
}

type MCPTool struct {
	Name        string          `json:"name"`
	Description string          `json:"description"`
	InputSchema json.RawMessage `json:"inputSchema"`
}

type MCPToolsListResponse struct {
	Tools []MCPTool `json:"tools"`
}

type MCPToolCallResponse struct {
	Content []MCPContent `json:"content"`
	IsError bool         `json:"isError,omitempty"`
}

type MCPContent struct {
	Type string `json:"type"`
	Text string `json:"text"`
}

// Tool parameter types
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

type ResetPortfolioParams struct {
	Confirm bool `json:"confirm"`
}

type TargetHolding struct {
	Ticker  string   `json:"ticker"`
	Name    string   `json:"name"`
	Weight  float64  `json:"weight"`
	Price   float64  `json:"price"`
	Comment *string  `json:"comment,omitempty"`
	Return  *float64 `json:"return,omitempty"`
}

type SetTargetPortfolioParams struct {
	Holdings []TargetHolding `json:"holdings"`
}

// Tool schemas
var GetHoldingsSchema = json.RawMessage(`{
	"type": "object",
	"properties": {},
	"required": []
}`)

var AddHoldingSchema = json.RawMessage(`{
	"type": "object",
	"properties": {
		"ticker": {"type": "string", "description": "Stock ticker symbol"},
		"name": {"type": "string", "description": "Company name"},
		"weight": {"type": "number", "description": "Portfolio weight percentage (0-100)"},
		"price": {"type": "number", "description": "Current stock price"},
		"comment": {"type": "string", "description": "Optional comment"},
		"return": {"type": "number", "description": "Optional return percentage"}
	},
	"required": ["ticker", "name", "weight", "price"]
}`)

var UpdateHoldingSchema = json.RawMessage(`{
	"type": "object",
	"properties": {
		"ticker": {"type": "string", "description": "Stock ticker symbol to update"},
		"name": {"type": "string", "description": "New company name"},
		"weight": {"type": "number", "description": "New portfolio weight percentage"},
		"price": {"type": "number", "description": "New stock price"},
		"comment": {"type": "string", "description": "New comment"},
		"return": {"type": "number", "description": "New return percentage"}
	},
	"required": ["ticker"]
}`)

var DeleteHoldingSchema = json.RawMessage(`{
	"type": "object",
	"properties": {
		"ticker": {"type": "string", "description": "Stock ticker symbol to delete"}
	},
	"required": ["ticker"]
}`)

var GetPortfolioSummarySchema = json.RawMessage(`{
	"type": "object",
	"properties": {},
	"required": []
}`)

var RebalanceHoldingsSchema = json.RawMessage(`{
	"type": "object",
	"properties": {
		"holdings": {
			"type": "array",
			"items": {
				"type": "object",
				"properties": {
					"ticker": {"type": "string"},
					"weight": {"type": "number"}
				},
				"required": ["ticker", "weight"]
			}
		}
	},
	"required": ["holdings"]
}`)

var ResetPortfolioSchema = json.RawMessage(`{
	"type": "object",
	"properties": {
		"confirm": {"type": "boolean", "description": "Confirmation flag"}
	},
	"required": ["confirm"]
}`)

var SetTargetPortfolioSchema = json.RawMessage(`{
	"type": "object",
	"properties": {
		"holdings": {
			"type": "array",
			"items": {
				"type": "object",
				"properties": {
					"ticker": {"type": "string"},
					"name": {"type": "string"},
					"weight": {"type": "number"},
					"price": {"type": "number"},
					"comment": {"type": "string"},
					"return": {"type": "number"}
				},
				"required": ["ticker", "name", "weight", "price"]
			}
		}
	},
	"required": ["holdings"]
}`)
