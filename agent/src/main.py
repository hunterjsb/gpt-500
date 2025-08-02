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
from .cli import (
    select_system_prompt,
    test_portfolio_db_connection,
    generate_markdown_from_database,
)
from .config import (
    CONNECTING_MCP_MSG,
    MCP_SUCCESS_MSG,
    MCP_ERROR_MSG,
    MCP_HELP_MSG,
    MIGRATION_PROMPT,
)


def main():
    # Allow user to select system prompt
    system_prompt_name, user_prompt_name = select_system_prompt()

    # Test portfolio-db server connection
    if not test_portfolio_db_connection():
        return

    # Connect to the MCP server and get portfolio tools
    print(CONNECTING_MCP_MSG)
    try:
        mcp_client = MCPClient(
            lambda: streamablehttp_client("http://localhost:8080/mcp")
        )

        with mcp_client:
            # Get portfolio tools from MCP server
            portfolio_tools = mcp_client.list_tools_sync()
            print(MCP_SUCCESS_MSG.format(len(portfolio_tools)))

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
                    generate_markdown_from_database()
            else:
                # Migration mode - let agent run with system prompt
                agent(MIGRATION_PROMPT)

                # After MIGRATION completes, also generate GPT20.md
                generate_markdown_from_database()

    except Exception as e:
        print(MCP_ERROR_MSG.format(e))
        print(MCP_HELP_MSG)
        return


if __name__ == "__main__":
    main()
