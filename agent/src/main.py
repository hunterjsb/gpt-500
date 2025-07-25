from strands import Agent
from strands.models.openai import OpenAIModel
from strands_tools import calculator

import os
from datetime import datetime
from .templates import load_template, format_template, read_index_for_update, write_index


def main():
    # Name of the index file to manage
    index_name = "GPT20"

    agent = Agent(
        model=OpenAIModel(client_args={"api_key": os.environ["OPENAI_API_KEY"]}, model_id="gpt-4o"),
        system_prompt=load_template("SYSTEM"),
        tools=[calculator]
    )

    # Read current index file
    current_index, file_exists = read_index_for_update(index_name)
    if file_exists:
        print(f"Current index file loaded ({len(current_index)} characters)")
    else:
        print("No existing index file found - will create new one")

    # Prepare the prompt for the agent
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prompt = format_template("UPDATE_PROMPT", current_time=current_time, current_index=current_index)

    # Get agent's response
    response = agent(prompt)

    # Extract the markdown content from the agent's response
    # The agent should provide the complete file content
    if response and hasattr(response, "content"):
        file_content = response.message
    else:
        file_content = str(response)

    # Write to the index file
    file_path = write_index(index_name, str(file_content))

    print(f"GPT20 index updated at {current_time}")
    print(f"File written to: {file_path}")


if __name__ == "__main__":
    main()
