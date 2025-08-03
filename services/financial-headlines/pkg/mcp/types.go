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
type GetGeneralHeadlinesParams struct{}

type GetStockHeadlinesParams struct {
	Ticker string `json:"ticker"`
}

type GetSectorHeadlinesParams struct {
	Sector string `json:"sector"`
}

type GetIndexHeadlinesParams struct {
	Index string `json:"index"`
}

// Tool schemas
var GetGeneralHeadlinesSchema = json.RawMessage(`{
	"type": "object",
	"properties": {},
	"required": []
}`)

var GetStockHeadlinesSchema = json.RawMessage(`{
	"type": "object",
	"properties": {
		"ticker": {"type": "string", "description": "Stock ticker symbol (e.g., AAPL)"}
	},
	"required": ["ticker"]
}`)

var GetSectorHeadlinesSchema = json.RawMessage(`{
	"type": "object",
	"properties": {
		"sector": {"type": "string", "description": "Market sector (e.g., Technology)"}
	},
	"required": ["sector"]
}`)

var GetIndexHeadlinesSchema = json.RawMessage(`{
	"type": "object",
	"properties": {
		"index": {"type": "string", "description": "Market index (e.g., S&P 500)"}
	},
	"required": ["index"]
}`)
