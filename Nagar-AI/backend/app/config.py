"""
NagarAI — Application Configuration
Reads settings from environment variables (docker-compose.yml injects these)
or falls back to defaults for local development.
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Default uses localhost — fine for local `python` execution.
    # Docker Compose overrides this via DATABASE_URL env var → postgres:5432
    DATABASE_URL: str = "postgresql://nagarai_user:nagarai_pass@localhost:5432/nagarai_db"
    SECRET_KEY: str = "nagarai-secret-key-2025-sih"
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
