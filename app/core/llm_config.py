"""LLM configuration for OpenRouter."""
from typing import Optional
from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def get_llm(temperature: Optional[float] = None) -> ChatOpenAI:
    """
    Create and return a ChatOpenAI instance configured for OpenRouter.
    
    Args:
        temperature: Override default temperature setting
        
    Returns:
        Configured ChatOpenAI instance
    """
    return ChatOpenAI(
        model=settings.llm_model,
        temperature=temperature or settings.llm_temperature,
        openai_api_key=settings.openrouter_api_key,
        openai_api_base=settings.openrouter_base_url,
        headers={
            "HTTP-Referer": "https://github.com/culi-ai/culi-backend",
            "X-Title": "Culi Backend",
        },
    )


def get_structured_llm(temperature: Optional[float] = None):
    """
    Get LLM configured for structured output (JSON mode).
    
    Args:
        temperature: Override default temperature setting
        
    Returns:
        Configured ChatOpenAI instance with JSON mode
    """
    llm = get_llm(temperature=temperature)
    # OpenRouter supports structured output via model parameters
    # We'll use this in prompts and tool definitions
    return llm

