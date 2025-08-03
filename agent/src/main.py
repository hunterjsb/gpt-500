import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from strands import Agent
from strands.models.openai import OpenAIModel
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from strands_tools import calculator, current_time, file_write, file_read, editor

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


class PortfolioUpdateWorkflow:
    """Structured workflow for portfolio updates with proper error handling."""

    def __init__(self):
        self.mcp_client = None
        self.agent = None
        self.strategy_path = "agent/md/notes/strategy.md"
        self.status = {"step": 0, "errors": [], "warnings": []}

    def log_status(self, message: str, level: str = "INFO"):
        """Log status with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = "✅" if level == "SUCCESS" else "❌" if level == "ERROR" else "⚠️" if level == "WARNING" else "ℹ️"
        print(f"[{timestamp}] {prefix} {message}")

        if level == "ERROR":
            self.status["errors"].append(message)
        elif level == "WARNING":
            self.status["warnings"].append(message)



    def read_strategy(self) -> Optional[str]:
        """Read current strategy document."""
        self.log_status("Step 1: Reading strategy document...")
        self.status["step"] = 1

        try:
            if Path(self.strategy_path).exists():
                with open(self.strategy_path, 'r') as f:
                    content = f.read()
                self.log_status(f"Strategy document loaded ({len(content)} chars)", "SUCCESS")
                return content
            else:
                self.log_status("Strategy document not found - will create new one", "WARNING")
                return None
        except Exception as e:
            self.log_status(f"Failed to read strategy: {e}", "ERROR")
            return None

    def get_portfolio_state(self) -> Optional[Dict]:
        """Get current portfolio holdings with retry logic."""
        self.log_status("Step 2: Getting current portfolio state...")
        self.status["step"] = 2

        assert self.mcp_client is not None, "MCP client not initialized"

        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Get holdings
                holdings_result = self.mcp_client.call_tool_sync("holdings_check", "get_holdings", {})
                if holdings_result and "content" in holdings_result and holdings_result["content"]:
                    content_item = holdings_result["content"][0]
                    if "text" in content_item:
                        holdings_data = json.loads(content_item["text"])
                    else:
                        raise Exception("No text in holdings result")

                    # Get summary
                    summary_result = self.mcp_client.call_tool_sync("summary_check", "get_portfolio_summary", {})
                    summary_data = {}
                    if summary_result and "content" in summary_result and summary_result["content"]:
                        content_item = summary_result["content"][0]
                        if "text" in content_item:
                            summary_data = json.loads(content_item["text"])

                    portfolio_state = {
                        "holdings": holdings_data,
                        "summary": summary_data,
                        "count": len(holdings_data)
                    }

                    self.log_status(f"Portfolio state retrieved - {portfolio_state['count']} holdings", "SUCCESS")
                    return portfolio_state
                else:
                    raise Exception("No content in holdings result")

            except Exception as e:
                self.log_status(f"Attempt {attempt + 1} failed: {e}", "WARNING")
                if attempt == max_retries - 1:
                    self.log_status("Failed to get portfolio state after all retries", "ERROR")
                    return None

        return None

    def get_market_data(self, tickers: List[str]) -> Optional[Dict]:
        """Get market data for specified tickers."""
        self.log_status("Step 3: Gathering market intelligence...")
        self.status["step"] = 3

        try:
            # Get market summary
            market_summary = get_market_summary()

            # Get stock info for current holdings
            tickers_str = ",".join(tickers[:10])  # Limit to avoid API limits
            stocks_info = get_multiple_stocks_info(tickers_str)

            market_data = {
                "market_summary": market_summary,
                "stocks_info": stocks_info,
                "timestamp": datetime.now().isoformat()
            }

            self.log_status(f"Market data retrieved for {len(tickers)} tickers", "SUCCESS")
            return market_data

        except Exception as e:
            self.log_status(f"Failed to get market data: {e}", "ERROR")
            return None

    def validate_portfolio_weights(self, portfolio: List[Dict]) -> Tuple[bool, str]:
        """Validate portfolio has exactly 20 holdings and weights sum to 100%."""
        if len(portfolio) != 20:
            return False, f"Portfolio has {len(portfolio)} holdings, need exactly 20"

        total_weight = sum(holding.get("weight", 0) for holding in portfolio)
        if abs(total_weight - 100.0) > 0.01:
            return False, f"Total weight is {total_weight:.3f}%, need exactly 100.000%"

        return True, f"Valid portfolio: 20 holdings, {total_weight:.3f}% total"

    def update_sector_holdings(self, sector_name: str, target_weight: float, current_holdings: List[Dict],
                              strategy: str, market_data: Dict) -> Optional[List[Dict]]:
        """Update holdings for a specific sector with simplified math."""
        self.log_status(f"Updating {sector_name} sector (target: {target_weight}% of portfolio)")

        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                current_sector_holdings = [h for h in current_holdings if sector_name.lower() in h.get('Comment', {}).get('String', '').lower()]
                current_sector_weight = sum(float(h.get('Weight', '0')) for h in current_sector_holdings)

                sector_prompt = f"""
{sector_name} sector target: {target_weight}%
Current sector weight: {current_sector_weight:.1f}%

Existing {sector_name} holdings:
{json.dumps(current_sector_holdings, indent=1)}

TASK: Return JSON array that totals exactly {target_weight}%.
Target stock count: {7 if sector_name == 'CORE' else 7 if sector_name == 'GROWTH' else 6} stocks
You can:
- Adjust weights of existing stocks
- Add new stocks to reach target
- Remove underperforming stocks

Format: {{"ticker":"MSFT","name":"Microsoft","weight":8.5,"price":524,"comment":"{sector_name}: reason"}}
Must sum to {target_weight}% with proper stock count:
"""

                local_tools = [calculator, get_stock_info, get_multiple_stocks_info]

                agent = Agent(
                    model=OpenAIModel(client_args={"api_key": API_KEY}, model_id=MODEL_ID),
                    system_prompt=f"Update {sector_name} sector. JSON only. Sum = {target_weight}%.",
                    tools=local_tools,
                )

                response = agent(sector_prompt)

                # Parse response
                response_text = str(response)
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1

                if start_idx == -1 or end_idx == 0:
                    raise ValueError("No JSON array found")

                json_str = response_text[start_idx:end_idx]
                sector_holdings = json.loads(json_str)

                # Validate sector weights
                sector_total = sum(h.get("weight", 0) for h in sector_holdings)
                if abs(sector_total - target_weight) > 0.1:
                    if attempt == 0:
                        self.log_status(f"{sector_name} attempt {attempt + 1}: {sector_total}% vs target {target_weight}%", "WARNING")
                        continue
                    else:
                        self.log_status(f"{sector_name} validation failed after retries", "ERROR")
                        return None

                self.log_status(f"{sector_name} sector updated: {len(sector_holdings)} holdings, {sector_total}%", "SUCCESS")
                return sector_holdings

            except Exception as e:
                self.log_status(f"{sector_name} attempt {attempt + 1} failed: {e}", "WARNING")

        return None

    def refined_portfolio_update_loop(self, strategy: str, portfolio_state: Dict, market_data: Dict) -> Optional[List[Dict]]:
        """Refined portfolio update loop with validation checkpoints."""
        self.log_status("Step 4: Refined portfolio update loop...")
        self.status["step"] = 4

        current_holdings = portfolio_state["holdings"]

        # Step 1: Add/Remove to get exactly 20 stocks
        target_stocks = self.adjust_stock_count(current_holdings, strategy, market_data)
        if target_stocks is None:
            return None

        # Step 2: Verify total count
        if len(target_stocks) != 20:
            self.log_status(f"Stock count error: {len(target_stocks)} instead of 20", "ERROR")
            return None
        self.log_status(f"✓ Stock count verified: {len(target_stocks)} stocks", "SUCCESS")

        # Step 3: Iterate over sectors to assign weights
        target_portfolio = self.assign_sector_weights(target_stocks, strategy)
        if target_portfolio is None:
            return None

        # Step 4: Verify total weights = 100%
        total_weight = sum(h.get("weight", 0) for h in target_portfolio)
        if abs(total_weight - 100.0) > 0.01:
            self.log_status(f"Weight error: {total_weight:.3f}% instead of 100%", "ERROR")
            return None
        self.log_status(f"✓ Weight verified: {total_weight:.3f}%", "SUCCESS")

        return target_portfolio

    def adjust_stock_count(self, current_holdings: List[Dict], strategy: str, market_data: Dict) -> Optional[List[Dict]]:
        """Add/remove stocks to get exactly 20."""
        self.log_status(f"Adjusting stock count from {len(current_holdings)} to 20...")

        current_tickers = [h["Ticker"] for h in current_holdings]
        target_tickers = current_tickers.copy()

        # If we have too many, remove worst performers
        while len(target_tickers) > 20:
            # Simple removal - remove last one (could be smarter)
            removed = target_tickers.pop()
            self.log_status(f"Removed {removed} (excess stock)")

        # If we have too few, let agent decide what to add
        if len(target_tickers) < 20:
            self.log_status(f"Need {20 - len(target_tickers)} more stocks - agent will decide")
            return None  # Let agent make decisions about which stocks to add

        # Create basic holdings structure
        target_stocks = []
        for ticker in target_tickers[:20]:
            # Find existing holding or create new one
            existing = next((h for h in current_holdings if h["Ticker"] == ticker), None)
            if existing:
                target_stocks.append({
                    "ticker": ticker,
                    "name": existing["Name"],
                    "price": float(existing["Price"]) if existing["Price"] != "0.0000" else 0.0,
                    "weight": 5.0  # Placeholder
                })
            else:
                target_stocks.append({
                    "ticker": ticker,
                    "name": f"{ticker} Corp",  # Placeholder
                    "price": 0.0,  # Will be updated
                    "weight": 5.0  # Placeholder
                })

        return target_stocks

    def assign_sector_weights(self, target_stocks: List[Dict], strategy: str) -> Optional[List[Dict]]:
        """Let agent assign sector-based weights to exactly 20 stocks."""
        self.log_status("Agent will assign sector-based weights...")

        # Agent should make these decisions, not hardcode them
        return None  # Return to agent-driven approach

    def make_portfolio_decisions(self, strategy: str, portfolio_state: Dict, market_data: Dict) -> Optional[List[Dict]]:
        """Use agent to make portfolio decisions with basic validation."""
        self.log_status("Step 4: Making portfolio decisions...")
        self.status["step"] = 4

        # Simple prompt for agent to construct exactly 20 stocks = 100%
        decision_prompt = f"""
Current portfolio has {len(portfolio_state['holdings'])} holdings.
Strategy: {strategy[:500]}...

Construct exactly 20 stocks totaling 100.000%.

Output JSON only:
[{{"ticker":"MSFT","name":"Microsoft","weight":8.0,"price":524,"comment":"reason"}}, ...]

Must be exactly 20 stocks, 100.000% total.
"""

        try:
            local_tools = [calculator, get_stock_info, get_multiple_stocks_info]

            agent = Agent(
                model=OpenAIModel(client_args={"api_key": API_KEY}, model_id=MODEL_ID),
                system_prompt="Portfolio manager. Output 20 stocks JSON. Total = 100%.",
                tools=local_tools,
            )

            response = agent(decision_prompt)

            # Parse JSON
            response_text = str(response)
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1

            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found")

            json_str = response_text[start_idx:end_idx]
            target_portfolio = json.loads(json_str)

            # Validate
            is_valid, message = self.validate_portfolio_weights(target_portfolio)
            if is_valid:
                self.log_status(message, "SUCCESS")
                return target_portfolio
            else:
                self.log_status(f"Validation failed: {message}", "ERROR")
                return None

        except Exception as e:
            self.log_status(f"Decision making failed: {e}", "ERROR")
            return None

    def execute_portfolio_update(self, target_portfolio: List[Dict]) -> bool:
        """Execute portfolio update with validation."""
        self.log_status("Step 5: Executing portfolio update...")
        self.status["step"] = 5

        assert self.mcp_client is not None, "MCP client not initialized"

        max_retries = 2
        for attempt in range(max_retries):
            try:
                # Prepare holdings for MCP call
                holdings_payload = []
                for holding in target_portfolio:
                    holdings_payload.append({
                        "ticker": holding["ticker"],
                        "name": holding["name"],
                        "weight": float(holding["weight"]),
                        "price": float(holding.get("price", 0)),
                        "comment": holding.get("comment", "")
                    })

                # Execute update
                result = self.mcp_client.call_tool_sync("portfolio_update", "set_target_portfolio", {"holdings": holdings_payload})

                if result and "content" in result:
                    self.log_status("Portfolio update executed successfully", "SUCCESS")

                    # Verify the update
                    verification = self.get_portfolio_state()
                    if verification and verification["count"] == 20:
                        self.log_status(f"Update verified - {verification['count']} holdings in database", "SUCCESS")
                        return True
                    else:
                        self.log_status("Update verification failed", "ERROR")
                        return False
                else:
                    raise Exception("No result from set_target_portfolio")

            except Exception as e:
                self.log_status(f"Update attempt {attempt + 1} failed: {e}", "WARNING")
                if attempt == max_retries - 1:
                    self.log_status("Portfolio update failed after all retries", "ERROR")
                    return False

        return False

    def update_strategy(self, strategy: str, changes: List[Dict], market_data: Dict) -> bool:
        """Update strategy document with changes."""
        self.log_status("Step 6: Updating strategy document...")
        self.status["step"] = 6

        try:
            # Create updated strategy content
            timestamp = datetime.now().strftime("%B %Y")

            updated_strategy = strategy + f"""

## Recent Updates ({timestamp})

### Portfolio Changes
"""
            for change in changes:
                updated_strategy += f"- {change.get('action', 'Updated')} {change.get('ticker', 'N/A')}: {change.get('reason', 'No reason provided')}\n"

            updated_strategy += f"""
### Market Assessment Update
- Market regime: {market_data.get('market_summary', {}).get('success', 'Unknown')}
- Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
- Next review: {(datetime.now()).strftime('%Y-%m-%d')} (quarterly)
"""

            # Write updated strategy
            Path(self.strategy_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.strategy_path, 'w') as f:
                f.write(updated_strategy)

            self.log_status("Strategy document updated", "SUCCESS")
            return True

        except Exception as e:
            self.log_status(f"Failed to update strategy: {e}", "ERROR")
            return False

    def generate_markdown(self) -> bool:
        """Generate markdown from database."""
        self.log_status("Step 7: Generating markdown output...")
        self.status["step"] = 7

        try:
            generate_markdown_from_database()
            self.log_status("Markdown generation completed", "SUCCESS")
            return True
        except Exception as e:
            self.log_status(f"Markdown generation failed: {e}", "ERROR")
            return False

    def run_workflow_with_mcp_context(self) -> bool:
        """Run the complete portfolio update workflow within MCP context."""
        self.log_status("=== Starting Portfolio Update Workflow ===")

        # Test portfolio-db connection first
        if not test_portfolio_db_connection():
            return False

        try:
            # Initialize MCP client
            self.mcp_client = MCPClient(
                lambda: streamablehttp_client("http://localhost:8080/mcp")
            )

            # Run entire workflow within MCP context
            with self.mcp_client:
                tools = self.mcp_client.list_tools_sync()
                self.log_status(f"MCP connection successful - {len(tools)} tools available", "SUCCESS")

                # Step 1: Read strategy
                strategy = self.read_strategy()
                if strategy is None:
                    self.log_status("Cannot proceed without strategy document", "ERROR")
                    return False

                # Step 2: Get portfolio state
                portfolio_state = self.get_portfolio_state()
                if portfolio_state is None:
                    return False

                # Step 3: Get market data
                current_tickers = [h["Ticker"] for h in portfolio_state["holdings"]]
                market_data = self.get_market_data(current_tickers)
                if market_data is None:
                    return False

                # Step 4: Make decisions
                target_portfolio = self.make_portfolio_decisions(strategy, portfolio_state, market_data)
                if target_portfolio is None:
                    return False

                # Step 5: Execute update
                if not self.execute_portfolio_update(target_portfolio):
                    return False

                # Step 6: Update strategy
                changes = [{"action": "Rebalanced", "ticker": "Portfolio", "reason": "Quarterly review and market analysis"}]
                if not self.update_strategy(strategy, changes, market_data):
                    self.log_status("Strategy update failed but portfolio was updated", "WARNING")

                # Step 7: Generate markdown
                if not self.generate_markdown():
                    self.log_status("Markdown generation failed but portfolio was updated", "WARNING")

                # Summary
                self.log_status("=== Portfolio Update Workflow Complete ===", "SUCCESS")
                self.log_status(f"Errors: {len(self.status['errors'])}, Warnings: {len(self.status['warnings'])}")

                if self.status["errors"]:
                    self.log_status("Errors encountered:", "ERROR")
                    for error in self.status["errors"]:
                        self.log_status(f"  - {error}", "ERROR")

                return len(self.status["errors"]) == 0

        except Exception as e:
            self.log_status(f"MCP workflow failed: {e}", "ERROR")
            return False


def main():
    """Main entry point with mode selection."""
    system_prompt_name, _ = select_system_prompt()

    if system_prompt_name == "MIGRATION":
        # Run migration mode (legacy)
        run_migration_mode()
    else:
        # Run structured workflow within MCP context
        workflow = PortfolioUpdateWorkflow()
        success = workflow.run_workflow_with_mcp_context()

        if not success:
            print("\n❌ Workflow failed. Check errors above.")
            sys.exit(1)
        else:
            print("\n✅ Portfolio update completed successfully!")


def run_migration_mode():
    """Legacy migration mode for initial setup."""
    print("🔄 Running migration mode...")

    if not test_portfolio_db_connection():
        return

    try:
        mcp_client = MCPClient(
            lambda: streamablehttp_client("http://localhost:8080/mcp")
        )

        with mcp_client:
            portfolio_tools = mcp_client.list_tools_sync()
            local_tools = [
                calculator,
                current_time,
                read_index,
                write_index,
                file_write,
                file_read,
                editor,
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
                system_prompt=load_template("MIGRATION"),
                tools=all_tools,
            )

            agent("Begin the migration process by reading the GPT20.md file and migrating the data to the database.")
            generate_markdown_from_database()

    except Exception as e:
        print(f"❌ Migration failed: {e}")


if __name__ == "__main__":
    main()
