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
    llm_model: str = "openai/gpt-4-turbo-preview"  # Default model for answer generation
    llm_temperature: float = 0.7
    
    # Model Selection - Optimized for cost and quality
    # Intent classification: cheap and fast
    llm_model_intent: str = "meta-llama/llama-3.1-8b-instruct"  # Extremely cheap, sufficient for classification
    
    # Plan generation: cheap for normal cases, free powerful model for complex cases
    llm_model_plan: str = "meta-llama/llama-3.1-8b-instruct"  # Default: cheap and capable
    llm_model_plan_complex: str = "nousresearch/hermes-3-llama-3.1-405b:free"  # Free powerful model for complex cases
    
    # Answer generation: quality for complex cases, cheap for simple ones
    llm_model_answer: str = "openai/gpt-4o-mini-2024-07-18"  # Good quality, cheaper than GPT-4, great for Vietnamese
    llm_model_answer_simple: str = "meta-llama/llama-3.1-8b-instruct"  # Very cheap for simple general_qa
    
    # Web search: LLM with built-in web search capability
    llm_model_web_search: str = "openai/gpt-4o-mini-search-preview"  # GPT-4o-mini with web search capability
    
    # Token limits - increased for better responses
    llm_max_tokens: int = 2000  # Default max tokens
    llm_max_tokens_intent: int = 200  # Intent classification needs less tokens
    llm_max_tokens_plan: int = 1000  # Plan generation
    llm_max_tokens_answer: int = 2000  # Answer generation needs more tokens
    llm_max_tokens_web_search: int = 2000  # Web search needs more tokens for comprehensive results
    
    # Chat History Configuration
    chat_history_length: int = 10  # Number of messages to include in context (increased from 3)

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
    
    # Plan Approval Configuration
    auto_approve_plans: bool = True  # Auto-approve plans for development/testing. Set to False when checkpoint mechanism is implemented.

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

