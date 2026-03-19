"""
NagarAI — Application Configuration
Reads settings from environment variables (docker-compose.yml injects these)
or falls back to defaults for local development.
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # These must be provided in .env or via environment variables
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: List[str] = ["*"]
    APP_NAME: str = "NagarAI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
