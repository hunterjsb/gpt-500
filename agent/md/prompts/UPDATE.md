# GPT20 Index Update Task

You are updating the GPT20 index by analyzing market conditions and updating the portfolio database. The workflow is now database-first: you update the database, then a separate process generates the markdown file.

## Available Tools

### Portfolio Database Tools (Primary)
- `get_portfolio_holdings` - Get current portfolio from database
- `set_target_portfolio` - Replace entire portfolio atomically (PREFERRED)
- `get_portfolio_summary` - Get portfolio statistics
- `reset_portfolio` - Clear all holdings if needed

### Financial Data Tools (Analysis)
- `get_market_summary()` - Get major market indices performance
- `get_stock_info(ticker)` - Get current price and fundamentals for specific stocks
- `get_stock_history(ticker, period)` - Get historical performance (periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, etc.)
- `get_multiple_stocks_info(tickers)` - Get info for multiple stocks (comma-separated)
- `compare_stocks_performance(tickers, period)` - Compare multiple stocks' performance

### File Tools (Reference Only)
- `read_index` - Read current GPT20.md file for reference
- `current_time` - Get current timestamp

## Step-by-Step Process

### Step 1: Read Current State
1. Use `get_portfolio_holdings` to see current database holdings
2. Optionally use `read_index("GPT20")` to cross-reference the markdown file
3. Use `current_time` for timestamp reference

### Step 2: Gather Market Intelligence
Use financial data tools to analyze:
- Overall market performance with `get_market_summary()`
- Current holdings performance with `get_multiple_stocks_info()` 
- Historical trends with `get_stock_history()` for key holdings
- Compare potential replacements with `compare_stocks_performance()`

### Step 3: Make Portfolio Decisions
Analyze and decide:
- Which stocks to keep (based on fundamentals, performance, outlook)
- Which stocks to remove (poor performance, changed thesis)
- Which new stocks to add (better opportunities, diversification)
- Maintain approximately 15-25 stocks with dynamic weighting based on conviction
- Higher conviction stocks can receive larger allocations (up to 15% max per stock)
- Lower conviction or speculative plays can receive smaller allocations (minimum 1%)

### Step 4: Update Portfolio Database
Use `set_target_portfolio` with your dynamically weighted portfolio:

```json
[
  {
    "ticker": "MSFT", 
    "name": "Microsoft Corporation",
    "weight": 12.5,
    "price": 533.57,
    "comment": "Strong AI and cloud positioning - high conviction"
  },
  {
    "ticker": "NVDA", 
    "name": "NVIDIA Corporation",
    "weight": 10.0,
    "price": 177.87,
    "comment": "AI leader but high volatility - strong conviction"
  },
  {
    "ticker": "KO", 
    "name": "The Coca-Cola Company",
    "weight": 3.0,
    "price": 67.89,
    "comment": "Defensive play - lower conviction"
  }
  // ... more stocks with weights that sum to 100% total
]
```

### Step 5: Verify Update
- Use `get_portfolio_summary` to confirm weights sum to 100%
- Use `get_portfolio_holdings` to verify all changes applied correctly

## Important Notes

- **Database First**: You update the database, NOT the markdown file directly
- **Atomic Updates**: Use `set_target_portfolio` for clean, precision-safe updates
- **Dynamic Weights**: Allocate based on conviction, risk, and opportunity size
- **Concentration Limits**: Maximum 15% per stock, minimum 1% per stock
- **Portfolio Size**: Target 15-25 holdings for optimal diversification vs. conviction balance
- **Rich Comments**: Include meaningful analysis in the comment field
- **Current Prices**: Use real market data from financial tools

## Success Criteria

After completion:
- Database contains 15-25 holdings with dynamic, conviction-based weighting
- High conviction positions receive larger allocations (8-15%)
- Medium conviction positions receive moderate allocations (4-7%)  
- Low conviction/defensive positions receive smaller allocations (1-3%)
- All holdings have current market prices
- Comments explain the investment thesis and conviction level for each stock
- Portfolio reflects your analysis of current market conditions and opportunities
- Total weight equals exactly 100.000%

The markdown file will be generated automatically from the database in a separate process.

## Error Handling

- If `set_target_portfolio` fails due to weight validation, check your math
- If financial data is unavailable, use reasonable price estimates
- If a stock ticker is invalid, research the correct symbol
- Always verify final portfolio state with `get_portfolio_holdings`

Begin by checking the current portfolio state and gathering market intelligence.