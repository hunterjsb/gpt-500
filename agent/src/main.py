from strands import Agent
from strands.models.openai import OpenAIModel
from strands_tools import calculator, current_time

from .templates import load_template
from .config import MODEL_ID, API_KEY
from .tools import read_index, write_index, get_index_info


def main():
    agent = Agent(
        model=OpenAIModel(client_args={"api_key": API_KEY}, model_id=MODEL_ID),
        system_prompt=load_template("SYSTEM"),
        tools=[calculator, current_time, read_index, write_index, get_index_info]
    )

    # Prepare the prompt for the agent using the template system
    prompt = load_template("UPDATE_PROMPT")

    # Get agent's response - let it handle everything
    response = agent(prompt)
    print("GPT20 index update completed")
    print("Agent response:", response)


if __name__ == "__main__":
    main()
