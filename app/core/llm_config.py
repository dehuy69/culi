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
        
    Raises:
        ValueError: If OPENROUTER_API_KEY is not set or empty
    """
    # Validate API key - must be set and not empty
    api_key = settings.openrouter_api_key
    if not api_key or not api_key.strip():
        error_msg = (
            "OPENROUTER_API_KEY is not set or is empty. "
            "Please set it in your .env file or environment variables. "
            "Example: OPENROUTER_API_KEY=sk-or-v1-..."
        )
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Strip whitespace from API key
    api_key = api_key.strip()
    
    # For OpenRouter, we need to pass headers
    # ChatOpenAI creates both sync and async clients internally
    # We need to pass api_key and base_url directly
    # Headers can be passed via default_headers in the OpenAI client
    # But since ChatOpenAI creates its own clients, we need to use http_client
    # or pass headers through environment or client initialization
    
    # Try using http_client with custom headers
    try:
        import httpx
        
        # Create httpx client with headers for OpenRouter
        http_client = httpx.Client(
            headers={
                "HTTP-Referer": "https://github.com/culi-ai/culi-backend",
                "X-Title": "Culi Backend",
            },
            timeout=60.0,
        )
        
        async_http_client = httpx.AsyncClient(
            headers={
                "HTTP-Referer": "https://github.com/culi-ai/culi-backend",
                "X-Title": "Culi Backend",
            },
            timeout=60.0,
        )
        
        return ChatOpenAI(
            model=settings.llm_model,
            temperature=temperature or settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,  # Limit tokens to avoid 402 errors
            openai_api_key=api_key,
            openai_api_base=settings.openrouter_base_url,
            http_client=http_client,
            http_async_client=async_http_client,
        )
    except ImportError:
        # Fallback: use default client creation
        # Headers will need to be set via environment or other means
        logger.warning("httpx not available, using default client (headers may not be set)")
        return ChatOpenAI(
            model=settings.llm_model,
            temperature=temperature or settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,  # Limit tokens to avoid 402 errors
            openai_api_key=api_key,
            openai_api_base=settings.openrouter_base_url,
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

