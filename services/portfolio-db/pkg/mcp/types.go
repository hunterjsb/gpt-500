package mcp

// MCP Protocol types
type Request struct {
	Method string      `json:"method"`
	Params interface{} `json:"params"`
}

type Response struct {
	Content []Content `json:"content"`
	IsError bool      `json:"isError,omitempty"`
}

type Content struct {
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