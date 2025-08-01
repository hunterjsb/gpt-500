"""Portfolio database tools via MCP."""

import requests
from typing import Dict, Any, List, Optional


def _call_mcp_tool(method: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call an MCP tool on the portfolio database server.

    Args:
        method: MCP method name
        params: Parameters for the method

    Returns:
        Response from the MCP server
    """
    url = "http://localhost:8080/mcp"
    payload = {"method": method, "params": params}

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"content": [{"type": "text", "text": f"Error calling MCP server: {e}"}], "isError": True}


def get_portfolio_holdings() -> Dict[str, Any]:
    """
    Get all current portfolio holdings from the database.

    Returns:
        dict with current holdings information
    """
    return _call_mcp_tool("get_holdings", {})


def add_portfolio_holding(
    ticker: str,
    name: str,
    weight: float,
    price: float,
    comment: Optional[str] = None,
    return_pct: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Add a new holding to the portfolio with automatic rebalancing.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL")
        name: Full company name
        weight: Desired weight percentage (0-100)
        price: Current stock price
        comment: Optional comment about the holding
        return_pct: Optional return percentage

    Returns:
        dict with operation result
    """
    params = {"ticker": ticker, "name": name, "weight": weight, "price": price}

    if comment:
        params["comment"] = comment
    if return_pct is not None:
        params["return"] = return_pct

    return _call_mcp_tool("add_holding", params)


def update_portfolio_holding(
    ticker: str,
    name: Optional[str] = None,
    weight: Optional[float] = None,
    price: Optional[float] = None,
    comment: Optional[str] = None,
    return_pct: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Update an existing portfolio holding.

    Args:
        ticker: Stock ticker symbol to update
        name: New company name (optional)
        weight: New weight percentage (optional)
        price: New stock price (optional)
        comment: New comment (optional)
        return_pct: New return percentage (optional)

    Returns:
        dict with operation result
    """
    params = {"ticker": ticker}

    if name is not None:
        params["name"] = name
    if weight is not None:
        params["weight"] = str(weight)
    if price is not None:
        params["price"] = str(price)
    if comment is not None:
        params["comment"] = comment
    if return_pct is not None:
        params["return"] = str(return_pct)

    return _call_mcp_tool("update_holding", params)


def delete_portfolio_holding(ticker: str) -> Dict[str, Any]:
    """
    Delete a holding from the portfolio.

    Args:
        ticker: Stock ticker symbol to delete

    Returns:
        dict with operation result
    """
    return _call_mcp_tool("delete_holding", {"ticker": ticker})


def get_portfolio_summary() -> Dict[str, Any]:
    """
    Get portfolio summary statistics.

    Returns:
        dict with portfolio summary (total weight, count, avg return)
    """
    return _call_mcp_tool("get_portfolio_summary", {})


def rebalance_portfolio_holdings(holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Rebalance multiple holdings in a single transaction.

    Args:
        holdings: List of dicts with 'ticker' and 'weight' keys

    Returns:
        dict with operation result
    """
    return _call_mcp_tool("rebalance_holdings", {"holdings": holdings})


def reset_portfolio(confirm: bool = True) -> Dict[str, Any]:
    """
    Reset the entire portfolio by removing all holdings.

    Args:
        confirm: Confirmation that you want to delete all holdings

    Returns:
        dict with operation result
    """
    return _call_mcp_tool("reset_portfolio", {"confirm": confirm})


def set_target_portfolio(holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Set the entire portfolio to the specified target holdings in one atomic operation.
    This replaces all existing holdings with the new target portfolio.

    Args:
        holdings: List of dicts with keys:
            - ticker: Stock ticker symbol (e.g., "AAPL")
            - name: Full company name
            - weight: Target weight percentage (0-100)
            - price: Current stock price
            - comment: Optional comment (optional)
            - return: Optional return percentage (optional)

    Returns:
        dict with operation result

    Example:
        holdings = [
            {"ticker": "AAPL", "name": "Apple Inc.", "weight": 5.0, "price": 150.0},
            {"ticker": "MSFT", "name": "Microsoft Corp.", "weight": 5.0, "price": 300.0},
            # ... 18 more stocks at 5% each = 100% total
        ]
    """
    return _call_mcp_tool("set_target_portfolio", {"holdings": holdings})
