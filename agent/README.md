# GPT20 Stock Index Agent

AI agent that maintains a curated list of 20 stocks in `md/indices/GPT20.md`.

## Setup

1. Set OpenAI API key:
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

2. Run manually:
   ```bash
   python -m agent
   ```

## Cron Setup

Add to crontab for automated updates:

```bash
# Set environment variables
OPENAI_API_KEY=your_openai_api_key_here
PATH=/usr/local/bin:/usr/bin:/bin

# Run weekdays at 4:30 PM (after market close)
30 16 * * 1-5 cd /path/to/agent && python -m agent >> gpt20.log 2>&1

# Or run daily at 8 PM
# 0 20 * * * cd /path/to/agent && python -m agent >> gpt20.log 2>&1
```

Install with: `crontab -e` then paste the above.

The agent reads the current GPT20.md file, analyzes market conditions, and updates the stock selections with rationale.