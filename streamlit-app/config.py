import os
from dotenv import load_dotenv

load_dotenv()

# Which LLM provider to use. One of: deepseek | groq | openrouter | gemini
# Each provider reads its own API key env var (see .env.example).
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "deepseek").lower()

APP_NAME = "SmartSchedule"
APP_VERSION = "1.2.0"
