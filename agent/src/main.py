import subprocess
import os
from strands import Agent
from strands.models.openai import OpenAIModel
from strands_tools import calculator, current_time

from .tools.templates import load_template
from .config import MODEL_ID, API_KEY
from .tools import (
    read_index, write_index, get_index_info,
    get_stock_info, get_stock_history, get_multiple_stocks_info,
    compare_stocks_performance, get_market_summary,
    get_portfolio_holdings, add_portfolio_holding, update_portfolio_holding,
    delete_portfolio_holding, get_portfolio_summary, reset_portfolio, set_target_portfolio
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

    agent = Agent(
        model=OpenAIModel(client_args={"api_key": API_KEY}, model_id=MODEL_ID),
        system_prompt=load_template(system_prompt_name),
        tools=[
            calculator, current_time,
            read_index, write_index, get_index_info,
            get_stock_info, get_stock_history, get_multiple_stocks_info,
            compare_stocks_performance, get_market_summary,
            get_portfolio_holdings, add_portfolio_holding, update_portfolio_holding,
            delete_portfolio_holding, get_portfolio_summary, reset_portfolio, set_target_portfolio
        ]
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
                    ["./generate-md"], 
                    cwd=portfolio_db_path,
                    capture_output=True,
                    text=True,
                    timeout=30
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
                ["./generate-md"], 
                cwd=portfolio_db_path,
                capture_output=True,
                text=True,
                timeout=30
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


if __name__ == "__main__":
    main()
