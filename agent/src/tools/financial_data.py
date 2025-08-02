"""Financial data tools using yfinance."""

import yfinance as yf
from datetime import datetime
from typing import Dict
from strands.tools.decorator import tool


@tool
def get_stock_info(ticker: str) -> Dict:
    """
    Get basic stock information and current price.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL")

    Returns:
        dict with stock information or error message
    """
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info

        # Extract key information
        result = {
            "ticker": ticker.upper(),
            "name": info.get("longName", "N/A"),
            "current_price": info.get("currentPrice"),
            "previous_close": info.get("previousClose"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "dividend_yield": info.get("dividendYield"),
            "52_week_high": info.get("fiftyTwoWeekHigh"),
            "52_week_low": info.get("fiftyTwoWeekLow"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "success": True,
        }

        # Calculate price change
        if result["current_price"] and result["previous_close"]:
            price_change = result["current_price"] - result["previous_close"]
            price_change_pct = (price_change / result["previous_close"]) * 100
            result["price_change"] = price_change
            result["price_change_pct"] = price_change_pct

        return result

    except Exception as e:
        return {
            "ticker": ticker.upper(),
            "success": False,
            "error": str(e),
            "message": f"Failed to get stock info for {ticker.upper()}: {str(e)}",
        }


@tool
def get_stock_history(ticker: str, period: str = "1mo") -> Dict:
    """
    Get historical stock price data.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL")
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

    Returns:
        dict with historical data or error message
    """
    try:
        stock = yf.Ticker(ticker.upper())
        hist = stock.history(period=period)

        if hist.empty:
            return {
                "ticker": ticker.upper(),
                "success": False,
                "error": "No historical data found",
                "message": f"No historical data available for {ticker.upper()}",
            }

        # Convert to simple format
        history_data = []
        for date, row in hist.iterrows():
            history_data.append(
                {
                    "date": str(date)[:10],
                    "open": round(float(row["Open"]), 2),
                    "high": round(float(row["High"]), 2),
                    "low": round(float(row["Low"]), 2),
                    "close": round(float(row["Close"]), 2),
                    "volume": int(row["Volume"]),
                }
            )

        # Calculate performance metrics
        first_close = hist["Close"].iloc[0]
        last_close = hist["Close"].iloc[-1]
        total_return = ((last_close - first_close) / first_close) * 100

        return {
            "ticker": ticker.upper(),
            "period": period,
            "data_points": len(history_data),
            "history": history_data,
            "total_return_pct": round(total_return, 2),
            "first_price": round(first_close, 2),
            "last_price": round(last_close, 2),
            "success": True,
        }

    except Exception as e:
        return {
            "ticker": ticker.upper(),
            "success": False,
            "error": str(e),
            "message": f"Failed to get historical data for {ticker.upper()}: {str(e)}",
        }


@tool
def get_multiple_stocks_info(tickers: str) -> Dict:
    """
    Get basic information for multiple stocks at once.

    Args:
        tickers: Comma-separated list of stock ticker symbols (e.g., "AAPL,MSFT,GOOGL")

    Returns:
        dict with information for each stock
    """
    ticker_list = [t.strip() for t in tickers.split(",")]
    results = {}
    failed_tickers = []

    for ticker in ticker_list:
        stock_info = get_stock_info(ticker)
        if stock_info["success"]:
            results[ticker.upper()] = stock_info
        else:
            failed_tickers.append(ticker.upper())

    return {
        "successful_count": len(results),
        "failed_count": len(failed_tickers),
        "failed_tickers": failed_tickers,
        "stocks": results,
        "success": len(results) > 0,
    }


@tool
def compare_stocks_performance(tickers: str, period: str = "1mo") -> Dict:
    """
    Compare performance of multiple stocks over a given period.

    Args:
        tickers: Comma-separated list of stock ticker symbols (e.g., "AAPL,MSFT,GOOGL")
        period: Time period for comparison (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

    Returns:
        dict with performance comparison
    """
    try:
        ticker_list = [t.strip() for t in tickers.split(",")]
        performance_data = []

        for ticker in ticker_list:
            hist_data = get_stock_history(ticker, period)
            if hist_data["success"]:
                performance_data.append(
                    {
                        "ticker": ticker.upper(),
                        "return_pct": hist_data["total_return_pct"],
                        "current_price": hist_data["last_price"],
                        "start_price": hist_data["first_price"],
                    }
                )

        # Sort by performance
        performance_data.sort(key=lambda x: x["return_pct"], reverse=True)

        return {
            "period": period,
            "stocks_compared": len(performance_data),
            "performance_ranking": performance_data,
            "best_performer": performance_data[0] if performance_data else None,
            "worst_performer": performance_data[-1] if performance_data else None,
            "success": len(performance_data) > 0,
        }

    except Exception as e:
        return {"success": False, "error": str(e), "message": f"Failed to compare stock performance: {str(e)}"}


@tool
def get_market_summary() -> Dict:
    """
    Get summary of major market indices.

    Returns:
        dict with market indices information
    """
    indices = {"S&P 500": "^GSPC", "Dow Jones": "^DJI", "NASDAQ": "^IXIC", "Russell 2000": "^RUT", "VIX": "^VIX"}

    market_data = {}

    for name, ticker in indices.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")  # Get last 2 days to calculate change

            if len(hist) >= 2:
                current = hist["Close"].iloc[-1]
                previous = hist["Close"].iloc[-2]
                change_pct = ((current - previous) / previous) * 100

                market_data[name] = {
                    "ticker": ticker,
                    "current_value": round(current, 2),
                    "previous_close": round(previous, 2),
                    "change_pct": round(change_pct, 2),
                    "success": True,
                }
            else:
                market_data[name] = {"ticker": ticker, "success": False, "error": "Insufficient data"}

        except Exception as e:
            market_data[name] = {"ticker": ticker, "success": False, "error": str(e)}

    successful_indices = sum(1 for data in market_data.values() if data.get("success"))

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "indices": market_data,
        "successful_count": successful_indices,
        "total_count": len(indices),
        "success": successful_indices > 0,
    }
