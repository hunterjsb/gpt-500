"""
Tools module for the GPT20 agent.

This module exports all available tools for use with the Strands agent framework.
"""

from strands.tools.decorator import tool
from .templates import _get_index_path, read_index_for_update as _read_index_for_update, write_index as _write_index
from .financial_data import (
    get_stock_info as _get_stock_info,
    get_stock_history as _get_stock_history,
    get_multiple_stocks_info as _get_multiple_stocks_info,
    compare_stocks_performance as _compare_stocks_performance,
    get_market_summary as _get_market_summary
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
        "message": f"Successfully read index file '{index_name}'" if exists else f"Index file '{index_name}' does not exist"
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
        "message": f"Successfully wrote {len(content)} characters to {file_path}"
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
            "message": f"Index file '{index_name}' exists with {len(content)} characters"
        }
    else:
        return {
            "exists": False,
            "path": str(index_path),
            "message": f"Index file '{index_name}' does not exist"
        }


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


# Export tools for easy import
__all__ = ['read_index', 'write_index', 'get_index_info', 'get_stock_info', 'get_stock_history',
           'get_multiple_stocks_info', 'compare_stocks_performance', 'get_market_summary']
