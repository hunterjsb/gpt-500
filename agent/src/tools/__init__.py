"""
Tools module for the GPT20 agent.

This module exports all available tools for use with the Strands agent framework.
"""

from typing import Optional
from strands.tools.decorator import tool
from .templates import _get_index_path, read_index_for_update as _read_index_for_update, write_index as _write_index
from .financial_data import (
    get_stock_info as _get_stock_info,
    get_stock_history as _get_stock_history,
    get_multiple_stocks_info as _get_multiple_stocks_info,
    compare_stocks_performance as _compare_stocks_performance,
    get_market_summary as _get_market_summary,
)
from .portfolio_db import (
    get_portfolio_holdings as _get_portfolio_holdings,
    add_portfolio_holding as _add_portfolio_holding,
    update_portfolio_holding as _update_portfolio_holding,
    delete_portfolio_holding as _delete_portfolio_holding,
    get_portfolio_summary as _get_portfolio_summary,
    reset_portfolio as _reset_portfolio,
    set_target_portfolio as _set_target_portfolio,
)


@tool
def read_index(index_name: str) -> dict:
    """
    Read an index file for updating.

    Args:
        index_name: Name of the index file (e.g., "GPT20")

    Returns:
        dict with 'content' and 'exists' keys
    """
    content, exists = _read_index_for_update(index_name)
    return {
        "content": content,
        "exists": exists,
        "message": (
            f"Successfully read index file '{index_name}'" if exists else f"Index file '{index_name}' does not exist"
        ),
    }


@tool
def write_index(index_name: str, content: str) -> dict:
    """
    Write content to an index file.

    Args:
        index_name: Name of the index file (e.g., "GPT20")
        content: Content to write to the file

    Returns:
        dict with success status and file path
    """
    file_path = _write_index(index_name, content)
    return {
        "success": True,
        "file_path": str(file_path),
        "message": f"Successfully wrote {len(content)} characters to {file_path}",
    }


@tool
def get_index_info(index_name: str) -> dict:
    """
    Get information about an index file.

    Args:
        index_name: Name of the index file (e.g., "GPT20")

    Returns:
        dict with file information
    """
    index_path = _get_index_path(index_name)

    if index_path.exists():
        content = index_path.read_text(encoding="utf-8")
        return {
            "exists": True,
            "path": str(index_path),
            "size_bytes": index_path.stat().st_size,
            "content_length": len(content),
            "line_count": len(content.splitlines()),
            "message": f"Index file '{index_name}' exists with {len(content)} characters",
        }
    else:
        return {"exists": False, "path": str(index_path), "message": f"Index file '{index_name}' does not exist"}


@tool
def get_stock_info(ticker: str) -> dict:
    """
    Get basic stock information and current price.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL")

    Returns:
        dict with stock information including price, market cap, ratios, etc.
    """
    return _get_stock_info(ticker)


@tool
def get_stock_history(ticker: str, period: str = "1mo") -> dict:
    """
    Get historical stock price data.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL")
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

    Returns:
        dict with historical price data and performance metrics
    """
    return _get_stock_history(ticker, period)


@tool
def get_multiple_stocks_info(tickers: str) -> dict:
    """
    Get basic information for multiple stocks at once.

    Args:
        tickers: Comma-separated list of stock ticker symbols (e.g., "AAPL,MSFT,GOOGL")

    Returns:
        dict with information for each stock
    """
    ticker_list = [t.strip() for t in tickers.split(",")]
    return _get_multiple_stocks_info(ticker_list)


@tool
def compare_stocks_performance(tickers: str, period: str = "1mo") -> dict:
    """
    Compare performance of multiple stocks over a given period.

    Args:
        tickers: Comma-separated list of stock ticker symbols (e.g., "AAPL,MSFT,GOOGL")
        period: Time period for comparison (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

    Returns:
        dict with performance comparison and rankings
    """
    ticker_list = [t.strip() for t in tickers.split(",")]
    return _compare_stocks_performance(ticker_list, period)


@tool
def get_market_summary() -> dict:
    """
    Get summary of major market indices (S&P 500, Dow Jones, NASDAQ, etc.).

    Returns:
        dict with current values and changes for major market indices
    """
    return _get_market_summary()


@tool
def get_portfolio_holdings() -> dict:
    """
    Get all current portfolio holdings from the database.

    Returns:
        dict with current holdings information
    """
    return _get_portfolio_holdings()


@tool
def add_portfolio_holding(ticker: str, name: str, weight: float, price: float, comment: Optional[str] = None) -> dict:
    """
    Add a new holding to the portfolio with automatic rebalancing.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL")
        name: Full company name
        weight: Desired weight percentage (0-100)
        price: Current stock price
        comment: Optional comment about the holding

    Returns:
        dict with operation result
    """
    # Convert empty string to None for optional comment
    actual_comment = comment if comment else None
    return _add_portfolio_holding(ticker, name, weight, price, actual_comment)


@tool
def update_portfolio_holding(
    ticker: str,
    name: Optional[str] = None,
    weight: Optional[float] = None,
    price: Optional[float] = None,
    comment: Optional[str] = None,
) -> dict:
    """
    Update an existing portfolio holding.

    Args:
        ticker: Stock ticker symbol to update
        name: New company name (optional)
        weight: New weight percentage (optional)
        price: New stock price (optional)
        comment: New comment (optional)

    Returns:
        dict with operation result
    """
    return _update_portfolio_holding(ticker, name, weight, price, comment)


@tool
def delete_portfolio_holding(ticker: str) -> dict:
    """
    Delete a holding from the portfolio.

    Args:
        ticker: Stock ticker symbol to delete

    Returns:
        dict with operation result
    """
    return _delete_portfolio_holding(ticker)


@tool
def get_portfolio_summary() -> dict:
    """
    Get portfolio summary statistics.

    Returns:
        dict with portfolio summary (total weight, count, avg return)
    """
    return _get_portfolio_summary()


@tool
def reset_portfolio(confirm: bool = True) -> dict:
    """
    Reset the entire portfolio by removing all holdings.

    Args:
        confirm: Confirmation that you want to delete all holdings

    Returns:
        dict with operation result
    """
    return _reset_portfolio(confirm)


@tool
def set_target_portfolio(holdings: str) -> dict:
    """
    Set the entire portfolio to the specified target holdings in one atomic operation.
    This replaces all existing holdings with the new target portfolio.

    Args:
        holdings: JSON string representing list of holdings, each with:
            - ticker: Stock ticker symbol (e.g., "AAPL")
            - name: Full company name
            - weight: Target weight percentage (0-100)
            - price: Current stock price
            - comment: Optional comment

    Returns:
        dict with operation result

    Example:
        holdings = '[{"ticker": "AAPL", "name": "Apple Inc.", "weight": 5.0, "price": 150.0}, {"ticker": "MSFT", "name": "Microsoft Corp.", "weight": 5.0, "price": 300.0}]'
    """
    import json

    holdings_list = json.loads(holdings)
    return _set_target_portfolio(holdings_list)


# Export tools for easy import
__all__ = [
    "read_index",
    "write_index",
    "get_index_info",
    "get_stock_info",
    "get_stock_history",
    "get_multiple_stocks_info",
    "compare_stocks_performance",
    "get_market_summary",
    "get_portfolio_holdings",
    "add_portfolio_holding",
    "update_portfolio_holding",
    "delete_portfolio_holding",
    "get_portfolio_summary",
    "reset_portfolio",
    "set_target_portfolio",
]
