"""Application configuration from environment variables."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/culi_db"

    # JWT Configuration
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # OpenRouter Configuration
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    llm_model: str = "openai/gpt-4-turbo-preview"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 250  # Limit max tokens to avoid 402 errors

    # Google Custom Search Configuration
    google_search_api_key: str = ""
    google_search_cx: str = ""

    # KiotViet OAuth2 Configuration
    kiotviet_token_url: str = "https://id.kiotviet.vn/connect/token"

    # Encryption Key for MCP client_secret (32 bytes)
    encryption_key: str = "your-32-byte-encryption-key-here-change-in-production"

    # Logging
    log_level: str = "INFO"

    # Application
    debug: bool = True
    app_name: str = "culi-backend"
    app_version: str = "0.1.0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

