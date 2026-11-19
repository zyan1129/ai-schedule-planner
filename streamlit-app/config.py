"""
SmartSchedule configuration.

Reads GEMINI_API_KEY from:
  1. Streamlit Cloud Secrets (st.secrets["GEMINI_API_KEY"]) — for deployment
  2. Local .env file (via python-dotenv)                    — for local dev
Streamlit Secrets wins when both are set.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # no-op in Streamlit Cloud


def _get_api_key() -> str:
    try:
        import streamlit as st
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY", "")


GEMINI_API_KEY = _get_api_key()
GEMINI_MODEL = "gemini-1.5-flash"  # fast + free tier friendly

APP_NAME = "SmartSchedule"
APP_VERSION = "1.1.0"
