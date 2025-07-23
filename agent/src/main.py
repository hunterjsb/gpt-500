from strands import Agent
from strands.models.openai import OpenAIModel
from strands_tools import calculator

from pathlib import Path
import os


def main():
    # Load system prompt from SYSTEM.md
    system_prompt_path = Path(__file__).parent.parent / "prompts" / "SYSTEM.md"
    system_prompt = system_prompt_path.read_text(encoding="utf-8")

    model = OpenAIModel(client_args={
        "api_key": os.environ["OPENAI_API_KEY"]
    },
    model_id="gpt-4o")

    agent = Agent(
        model=model,
        system_prompt=system_prompt,
        tools=[calculator]
    )

    response = agent("What is 2+2")
    print(response)


if __name__ == "__main__":
    main()
