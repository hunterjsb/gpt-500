from strands import Agent
from strands.models.openai import OpenAIModel
from strands_tools import calculator

from pathlib import Path
import os
from datetime import datetime
from .templates import load_system_prompt, load_update_prompt


def main():
    # Load system prompt
    system_prompt = load_system_prompt()

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
    prompt = load_update_prompt(current_time, current_index)

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
