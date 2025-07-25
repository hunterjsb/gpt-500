from strands import Agent
from strands.models.openai import OpenAIModel
from strands_tools import calculator, current_time

from .tools.templates import load_template
from .config import MODEL_ID, API_KEY
from .tools import read_index, write_index, get_index_info


def main():
    agent = Agent(
        model=OpenAIModel(client_args={"api_key": API_KEY}, model_id=MODEL_ID),
        system_prompt=load_template("SYSTEM"),
        tools=[calculator, current_time, read_index, write_index, get_index_info]
    )

    # update the index, it should use its tools to read & write to the file
    prompt = load_template("UPDATE_PROMPT")
    agent(prompt)


if __name__ == "__main__":
    main()
