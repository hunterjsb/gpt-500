import subprocess
import requests
from strands import Agent
from strands.models.openai import OpenAIModel
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from strands_tools import calculator, current_time

from .tools.templates import load_template
from .config import MODEL_ID, API_KEY
from .tools import (
    read_index,
    write_index,
    get_index_info,
    get_stock_info,
    get_stock_history,
    get_multiple_stocks_info,
    compare_stocks_performance,
    get_market_summary,
)


def main():
    # Allow user to select system prompt
    print("Available system prompts:")
    print("1. SYSTEM - Standard GPT20 index management")
    print("2. MIGRATION - Migrate GPT20.md to database")

    choice = input("Select prompt (1 or 2): ").strip()

    if choice == "2":
        system_prompt_name = "MIGRATION"
        user_prompt_name = None  # Migration prompt is self-contained
        print("Using MIGRATION system prompt...")
    else:
        system_prompt_name = "SYSTEM"
        user_prompt_name = "UPDATE"
        print("Using SYSTEM prompt with UPDATE...")

    # Test portfolio-db server connection
    print("Testing portfolio-db server connection...")
    try:
        response = requests.get("http://localhost:8080/health", timeout=5)
        response.raise_for_status()
        print("✅ Portfolio-db server is running")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to portfolio-db server: {e}")
        print("Make sure the portfolio-db server is running on localhost:8080")
        print("You can start it with: cd services/portfolio-db && ./start_server.sh")
        return

    # Connect to the MCP server and get portfolio tools
    print("Connecting to portfolio-db MCP server...")
    try:
        mcp_client = MCPClient(
            lambda: streamablehttp_client("http://localhost:8080/mcp")
        )

        with mcp_client:
            # Get portfolio tools from MCP server
            portfolio_tools = mcp_client.list_tools_sync()
            print(f"✅ Loaded {len(portfolio_tools)} portfolio tools from MCP server")

            # Combine local tools with MCP portfolio tools
            local_tools = [
                calculator,
                current_time,
                read_index,
                write_index,
                get_index_info,
                get_stock_info,
                get_stock_history,
                get_multiple_stocks_info,
                compare_stocks_performance,
                get_market_summary,
            ]

            all_tools = local_tools + portfolio_tools

            agent = Agent(
                model=OpenAIModel(client_args={"api_key": API_KEY}, model_id=MODEL_ID),
                system_prompt=load_template(system_prompt_name),
                tools=all_tools,
            )

            if user_prompt_name:
                # Standard index update
                prompt = load_template(user_prompt_name)
                agent(prompt)

                # After UPDATE completes, automatically generate GPT20.md from database
                if system_prompt_name == "SYSTEM":
                    print("\n🚀 Generating GPT20.md from updated database...")
                    try:
                        # Path to the portfolio-db service
                        portfolio_db_path = "/home/hunter/Desktop/claude-20/services/portfolio-db"
                        result = subprocess.run(
                            ["./generate-md"], cwd=portfolio_db_path, capture_output=True, text=True, timeout=30
                        )

                        if result.returncode == 0:
                            print("✅ GPT20.md successfully generated!")
                            print(result.stdout.strip())
                        else:
                            print(f"❌ Error generating markdown: {result.stderr}")

                    except subprocess.TimeoutExpired:
                        print("❌ Timeout: Markdown generation took too long")
                    except Exception as e:
                        print(f"❌ Failed to generate markdown: {e}")
            else:
                # Migration mode - let agent run with system prompt
                agent("Begin the migration process by reading the GPT20.md file and migrating the data to the database.")

                # After MIGRATION completes, also generate GPT20.md
                print("\n🚀 Generating GPT20.md from migrated database...")
                try:
                    portfolio_db_path = "/home/hunter/Desktop/claude-20/services/portfolio-db"
                    result = subprocess.run(
                        ["./generate-md"], cwd=portfolio_db_path, capture_output=True, text=True, timeout=30
                    )

                    if result.returncode == 0:
                        print("✅ GPT20.md successfully generated!")
                        print(result.stdout.strip())
                    else:
                        print(f"❌ Error generating markdown: {result.stderr}")

                except subprocess.TimeoutExpired:
                    print("❌ Timeout: Markdown generation took too long")
                except Exception as e:
                    print(f"❌ Failed to generate markdown: {e}")

    except Exception as e:
        print(f"❌ Failed to connect to MCP server: {e}")
        print("Make sure the portfolio-db server is running and properly configured for MCP")
        return


if __name__ == "__main__":
    main()
