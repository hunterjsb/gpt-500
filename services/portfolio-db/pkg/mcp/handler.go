package mcp

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
)

type PortfolioService interface {
	GetHoldings(ctx context.Context, params GetHoldingsParams) (*Response, error)
	AddHolding(ctx context.Context, params AddHoldingParams) (*Response, error)
	UpdateHolding(ctx context.Context, params UpdateHoldingParams) (*Response, error)
	DeleteHolding(ctx context.Context, params DeleteHoldingParams) (*Response, error)
	GetPortfolioSummary(ctx context.Context, params GetPortfolioSummaryParams) (*Response, error)
	RebalanceHoldings(ctx context.Context, params RebalanceHoldingsParams) (*Response, error)
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

	var req Request
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	ctx := r.Context()
	var response *Response
	var err error

	switch req.Method {
	case "get_holdings":
		var params GetHoldingsParams
		response, err = h.portfolioService.GetHoldings(ctx, params)

	case "add_holding":
		var params AddHoldingParams
		if paramsBytes, marshalErr := json.Marshal(req.Params); marshalErr == nil {
			json.Unmarshal(paramsBytes, &params)
		}
		response, err = h.portfolioService.AddHolding(ctx, params)

	case "update_holding":
		var params UpdateHoldingParams
		if paramsBytes, marshalErr := json.Marshal(req.Params); marshalErr == nil {
			json.Unmarshal(paramsBytes, &params)
		}
		response, err = h.portfolioService.UpdateHolding(ctx, params)

	case "delete_holding":
		var params DeleteHoldingParams
		if paramsBytes, marshalErr := json.Marshal(req.Params); marshalErr == nil {
			json.Unmarshal(paramsBytes, &params)
		}
		response, err = h.portfolioService.DeleteHolding(ctx, params)

	case "get_portfolio_summary":
		var params GetPortfolioSummaryParams
		response, err = h.portfolioService.GetPortfolioSummary(ctx, params)

	case "rebalance_holdings":
		var params RebalanceHoldingsParams
		if paramsBytes, marshalErr := json.Marshal(req.Params); marshalErr == nil {
			json.Unmarshal(paramsBytes, &params)
		}
		response, err = h.portfolioService.RebalanceHoldings(ctx, params)

	default:
		response = &Response{
			Content: []Content{{Type: "text", Text: fmt.Sprintf("Unknown method: %s", req.Method)}},
			IsError: true,
		}
	}

	if err != nil {
		response = &Response{
			Content: []Content{{Type: "text", Text: fmt.Sprintf("Internal error: %v", err)}},
			IsError: true,
		}
	}

	json.NewEncoder(w).Encode(response)
}