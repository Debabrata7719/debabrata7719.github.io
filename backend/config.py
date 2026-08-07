"""
config.py — Application configuration via environment variables.

Loads RESEND_API_KEY and MAIL_TO from the .env file located one
directory above this file (i.e. portfolio_V2/.env).
"""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Portfolio backend settings.

    All fields are read from environment variables / .env file.
    """

    resend_api_key: str
    mail_to: str

    model_config = {
        # Resolve the .env file relative to the project root, not this file
        "env_file": str(Path(__file__).resolve().parent.parent / ".env"),
        "env_file_encoding": "utf-8",
    }


# Single shared instance — import this everywhere
settings = Settings()
