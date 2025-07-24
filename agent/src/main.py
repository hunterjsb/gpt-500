from strands import Agent
from strands.models.openai import OpenAIModel
from strands_tools import calculator

from pathlib import Path
import os
from datetime import datetime


def main():
    # Load system prompt from SYSTEM.md
    system_prompt_path = Path(__file__).parent.parent / "md" / "prompts" / "SYSTEM.md"
    system_prompt = system_prompt_path.read_text(encoding="utf-8")

    # Path to the GPT20 index file
    index_file_path = Path(__file__).parent.parent / "md" / "indices" / "GPT20.md"

    model = OpenAIModel(client_args={
        "api_key": os.environ["OPENAI_API_KEY"]
    },
    model_id="gpt-4o")

    agent = Agent(
        model=model,
        system_prompt=system_prompt,
        tools=[calculator]
    )

    # Read current index file if it exists
    current_index = ""
    if index_file_path.exists():
        current_index = index_file_path.read_text(encoding="utf-8")
        print(f"Current index file loaded ({len(current_index)} characters)")
    else:
        print("No existing index file found - will create new one")

    # Prepare the prompt for the agent
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    prompt = f"""
Current time: {current_time}

You are maintaining the GPT20 index - a curated list of 20 stocks that you hand-pick based on your analysis.

Current GPT20.md content:
{current_index if current_index else "FILE IS EMPTY - CREATE THE INITIAL INDEX"}

Your task:
1. Read and analyze the current state of the GPT20 index
2. Think about market conditions, recent events, and stock performance
3. Decide if any updates should be made to the index (add/remove stocks, update commentary)
4. Write the complete updated GPT20.md file content

The file should contain:
- A brief header explaining what GPT20 is
- List of 20 stocks with ticker symbols
- Brief rationale for each selection or recent changes
- Last updated timestamp

Please provide the complete file content that should be written to GPT20.md.
"""

    # Get agent's response
    response = agent(prompt)

    # Extract the markdown content from the agent's response
    # The agent should provide the complete file content
    if response and hasattr(response, 'content'):
        file_content = response.message
    else:
        file_content = str(response)

    # Write to the index file
    index_file_path.parent.mkdir(parents=True, exist_ok=True)
    index_file_path.write_text(str(file_content), encoding="utf-8")

    print(f"GPT20 index updated at {current_time}")
    print(f"File written to: {index_file_path}")


if __name__ == "__main__":
    main()
