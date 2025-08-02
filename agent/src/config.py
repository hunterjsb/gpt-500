"""Configuration settings for the agent."""

import os

# Model configuration
MODEL_ID = "gpt-4o"
API_KEY = os.environ.get("OPENAI_API_KEY")

# Index file configuration
INDEX_NAME = "GPT20"

# CLI Messages
PROMPT_MENU = """Available system prompts:
1. SYSTEM - Standard GPT20 index management
2. MIGRATION - Migrate GPT20.md to database"""

PROMPT_INPUT = "Select prompt (1 or 2): "
USING_MIGRATION_MSG = "Using MIGRATION system prompt..."
USING_SYSTEM_MSG = "Using SYSTEM prompt with UPDATE..."
TESTING_CONNECTION_MSG = "Testing portfolio-db server connection..."
CONNECTION_SUCCESS_MSG = "✅ Portfolio-db server is running"
CONNECTION_ERROR_MSG = "❌ Failed to connect to portfolio-db server: {}"
CONNECTION_HELP_MSG = """Make sure the portfolio-db server is running on localhost:8080
You can start it with: cd services/portfolio-db && ./start_server.sh"""
CONNECTING_MCP_MSG = "Connecting to portfolio-db MCP server..."
MCP_SUCCESS_MSG = "✅ Loaded {} portfolio tools from MCP server"
MCP_ERROR_MSG = "❌ Failed to connect to MCP server: {}"
MCP_HELP_MSG = "Make sure the portfolio-db server is running and properly configured for MCP"
GENERATING_MD_MSG = "\n🚀 Generating GPT20.md from updated database..."
MD_SUCCESS_MSG = "✅ GPT20.md successfully generated!"
MD_ERROR_MSG = "❌ Error generating markdown: {}"
MD_TIMEOUT_MSG = "❌ Timeout: Markdown generation took too long"
MD_FAILED_MSG = "❌ Failed to generate markdown: {}"
MIGRATION_PROMPT = "Begin the migration process by reading the GPT20.md file and migrating the data to the database."
