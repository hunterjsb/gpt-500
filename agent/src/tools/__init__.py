"""
Tools module for the GPT20 agent.

This module exports all available tools for use with the Strands agent framework.
"""

# Import decorated tools from their respective modules
from .financial_data import (
    get_stock_info,
    get_stock_history,
    get_multiple_stocks_info,
    compare_stocks_performance,
    get_market_summary,
)
from .templates import (
    read_index,
    write_index,
    get_index_info,
)

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
]
