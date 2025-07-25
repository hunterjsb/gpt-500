"""Configuration settings for the agent."""

import os

# Model configuration
MODEL_ID = "gpt-4o"
API_KEY = os.environ.get("OPENAI_API_KEY")

# Index file configuration
INDEX_NAME = "GPT20"

# Time format
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
