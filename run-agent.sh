#!/bin/bash

# GPT20 Agent Runner - Convenience script to start portfolio-db and run the agent

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 GPT20 Agent Runner${NC}"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "agent" ] || [ ! -d "services/portfolio-db" ]; then
    echo -e "${RED}❌ Error: Must run from the claude-20 project root directory${NC}"
    exit 1
fi

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Step 1: Check/Start Portfolio Database Server
echo -e "${YELLOW}📊 Checking portfolio database server...${NC}"

if check_port 8080; then
    echo -e "${GREEN}✅ Portfolio-db server already running on port 8080${NC}"
else
    echo -e "${YELLOW}🚀 Starting portfolio-db server...${NC}"

    # Navigate to portfolio-db directory
    cd services/portfolio-db

    # Check if binary exists, build if needed
    if [ ! -f "portfolio-db" ]; then
        echo -e "${YELLOW}🔨 Building portfolio-db server...${NC}"
        go build -o portfolio-db || {
            echo -e "${RED}❌ Failed to build portfolio-db server${NC}"
            exit 1
        }
    fi

    # Start the server in background
    nohup ./portfolio-db > server.log 2>&1 &
    SERVER_PID=$!

    # Wait for server to start
    echo -e "${YELLOW}⏳ Waiting for server to start...${NC}"
    sleep 3

    # Check if server is running
    if check_port 8080; then
        echo -e "${GREEN}✅ Portfolio-db server started successfully (PID: $SERVER_PID)${NC}"
    else
        echo -e "${RED}❌ Failed to start portfolio-db server${NC}"
        echo "Check server.log for details:"
        tail -10 server.log
        exit 1
    fi

    # Return to project root
    cd ../..
fi

# Step 2: Health check
echo -e "${YELLOW}🏥 Performing health check...${NC}"
if curl -f -s http://localhost:8080/health > /dev/null; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed - server may not be ready${NC}"
    exit 1
fi

# Step 3: Check Python environment
echo -e "${YELLOW}🐍 Checking Python environment...${NC}"

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  Not in a virtual environment${NC}"
    echo -e "${YELLOW}💡 Consider activating your venv: source venv/bin/activate${NC}"
fi

# Check for required packages
if ! python3 -c "import strands, yfinance, requests" 2>/dev/null; then
    echo -e "${RED}❌ Missing required Python packages${NC}"
    echo "Install with: pip install strands yfinance requests"
    exit 1
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}❌ OPENAI_API_KEY environment variable not set${NC}"
    echo "Set it with: export OPENAI_API_KEY='your-key-here'"
    exit 1
fi

echo -e "${GREEN}✅ Python environment ready${NC}"

# Step 4: Run the agent
echo ""
echo -e "${BLUE}🤖 Starting GPT20 Agent...${NC}"
echo "=================================="

# Navigate to agent directory and run
cd agent
python3 -m src.main

echo ""
echo -e "${GREEN}✅ Agent execution completed!${NC}"

# Step 5: Show results
echo ""
echo -e "${BLUE}📊 Portfolio Summary${NC}"
echo "=================================="

# Try to get portfolio summary via API
echo "Current portfolio status:"
curl -s -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "get_portfolio_summary", "arguments": {}}}' | \
  python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if 'result' in data and 'content' in data['result']:
        print(data['result']['content'][0]['text'])
    else:
        print('No portfolio data available')
except:
    print('Could not retrieve portfolio summary')
"

echo ""
echo -e "${GREEN}🎉 Done! Check the updated portfolio at:${NC}"
echo -e "${BLUE}   📁 agent/md/indices/GPT20.md${NC}"
echo -e "${BLUE}   🌐 https://hunterjsb.github.io/gpt-500/${NC}"
echo ""
echo -e "${YELLOW}💡 To stop the portfolio-db server:${NC}"
echo "   pkill -f portfolio-db"
