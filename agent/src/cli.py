import subprocess
import requests
from typing import Optional, Tuple

from .config import (
    PROMPT_MENU,
    PROMPT_INPUT,
    USING_MIGRATION_MSG,
    USING_SYSTEM_MSG,
    TESTING_CONNECTION_MSG,
    CONNECTION_SUCCESS_MSG,
    CONNECTION_ERROR_MSG,
    CONNECTION_HELP_MSG,
    GENERATING_MD_MSG,
    MD_SUCCESS_MSG,
    MD_ERROR_MSG,
    MD_TIMEOUT_MSG,
    MD_FAILED_MSG,
)


def select_system_prompt() -> Tuple[str, Optional[str]]:
    """
    Allow user to select system prompt and return the appropriate configuration.

    Returns:
        Tuple of (system_prompt_name, user_prompt_name)
    """
    print(PROMPT_MENU)

    choice = input(PROMPT_INPUT).strip()

    if choice == "2":
        system_prompt_name = "MIGRATION"
        user_prompt_name = None  # Migration prompt is self-contained
        print(USING_MIGRATION_MSG)
    else:
        system_prompt_name = "SYSTEM"
        user_prompt_name = "UPDATE"
        print(USING_SYSTEM_MSG)

    return system_prompt_name, user_prompt_name


def test_portfolio_db_connection() -> bool:
    """
    Test connection to the portfolio-db server.

    Returns:
        True if connection successful, False otherwise
    """
    print(TESTING_CONNECTION_MSG)
    try:
        response = requests.get("http://localhost:8080/health", timeout=5)
        response.raise_for_status()
        print(CONNECTION_SUCCESS_MSG)
        return True
    except requests.exceptions.RequestException as e:
        print(CONNECTION_ERROR_MSG.format(e))
        print(CONNECTION_HELP_MSG)
        return False


def generate_markdown_from_database() -> None:
    """
    Generate GPT20.md from the updated database by calling the generate-md script.
    """
    print(GENERATING_MD_MSG)
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
            print(MD_SUCCESS_MSG)
            print(result.stdout.strip())
        else:
            print(MD_ERROR_MSG.format(result.stderr))

    except subprocess.TimeoutExpired:
        print(MD_TIMEOUT_MSG)
    except Exception as e:
        print(MD_FAILED_MSG.format(e))
