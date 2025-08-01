# Portfolio Database MCP Server

A Model Context Protocol (MCP) server that exposes GPT-500 portfolio database operations as tools for Strands agents.

## Features

- **CRUD Operations**: Create, read, update, delete portfolio holdings
- **Portfolio Validation**: Enforces 100% weight constraint via database triggers
- **HTTP-based**: Compatible with Strands `streamablehttp_client`
- **Lambda Ready**: Designed for AWS Lambda deployment

## Available Tools

### get_holdings
Returns all portfolio holdings sorted by weight.

**Parameters:** None

**Response:** JSON array of holdings with ticker, name, weight, price, returns, etc.

### add_holding
Adds a new holding to the portfolio.

**Parameters:**
- `ticker` (string): Stock ticker symbol (e.g., "AAPL")
- `name` (string): Full company name
- `weight` (float64): Portfolio weight percentage (0-100)
- `price` (float64): Current stock price
- `comment` (string, optional): Notes about the holding
- `return` (float64, optional): Cumulative return percentage

### update_holding
Updates an existing holding's properties.

**Parameters:**
- `ticker` (string): Stock ticker to update
- `name` (string, optional): New company name
- `weight` (float64, optional): New weight percentage
- `price` (float64, optional): New stock price
- `comment` (string, optional): New comment
- `return` (float64, optional): New return percentage

### delete_holding
Removes a holding from the portfolio.

**Parameters:**
- `ticker` (string): Stock ticker to remove

### get_portfolio_summary
Returns portfolio summary statistics.

**Parameters:** None

**Response:** JSON with total_weight, holding_count, avg_return

## Database Schema

Uses the `portfolio_holdings` table with constraint trigger ensuring weights sum to 100%.

## Usage with Strands Agents

```python
from strands import Agent
from strands.mcp import MCPClient, streamablehttp_client

# Connect to the MCP server
mcp_client = MCPClient(
    lambda: streamablehttp_client("http://localhost:8080/mcp")
)

with mcp_client:
    tools = mcp_client.list_tools_sync()
    agent = Agent(tools=tools)
    
    # Agent can now use portfolio database tools
    response = agent.chat("Show me the current portfolio holdings")
```

## Environment Variables

- `DB_HOST`: PostgreSQL host (default: localhost)
- `DB_PORT`: PostgreSQL port (default: 5432)  
- `DB_USER`: Database username (default: hunter)
- `DB_PASSWORD`: Database password (default: postgres)
- `DB_NAME`: Database name (default: gpt_500)
- `PORT`: HTTP server port (default: 8080)

## Running Locally

```bash
# Install dependencies
go mod tidy

# Set environment variables
export DB_PASSWORD=postgres

# Run the server
go run main.go
```

## Testing

```bash
# Health check
curl http://localhost:8080/health

# Get holdings
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "get_holdings", "params": {}}'

# Add holding
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "add_holding", 
    "params": {
      "ticker": "AAPL",
      "name": "Apple Inc.",
      "weight": 25.0,
      "price": 150.25
    }
  }'
```

## Lambda Deployment

This service is designed to be deployed as an AWS Lambda function with API Gateway for HTTP access. The agent will be able to discover and use these tools over HTTP.