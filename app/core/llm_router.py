"""LLM model router for dynamic model selection based on task complexity."""
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def get_model_for_intent_router(state: Optional[Dict[str, Any]] = None) -> str:
    """
    Get model for intent classification.
    
    Requirements: Fast, cheap, smart enough for classification.
    
    Returns:
        Model identifier for OpenRouter
    """
    # Always use Llama-3.1-8B for intent classification
    # It's extremely cheap and sufficient for this task
    model = settings.llm_model_intent or "meta-llama/llama-3.1-8b-instruct"
    logger.debug(f"Intent router model: {model}")
    return model


def get_model_for_app_plan(state: Optional[Dict[str, Any]] = None) -> str:
    """
    Get model for plan generation.
    
    Requirements: Good reasoning, understands business logic, generates valid JSON.
    
    Strategy:
    - Normal cases: Llama-3.1-8B (cheap and sufficient)
    - Complex cases: Hermes-3 405B free (powerful and free)
    
    Args:
        state: Current graph state to determine complexity
        
    Returns:
        Model identifier for OpenRouter
    """
    # Check if we should use free powerful model for complex cases
    if state:
        user_input = state.get("user_input", "")
        intent = state.get("intent", "")
        
        # Use Hermes-3 free for very complex cases
        # Criteria: long input (>800 chars) or explicitly complex intent
        is_complex = (
            len(user_input) > 800 or
            intent == "app_plan" and len(user_input) > 500
        )
        
        if is_complex and settings.llm_model_plan_complex:
            model = settings.llm_model_plan_complex
            logger.info(f"Using complex model for app_plan: {model} (input length: {len(user_input)})")
            return model
    
    # Default: use cheap but capable model
    model = settings.llm_model_plan or "meta-llama/llama-3.1-8b-instruct"
    logger.debug(f"App plan model: {model}")
    return model


def get_model_for_answer(state: Optional[Dict[str, Any]] = None) -> str:
    """
    Get model for answer generation.
    
    Requirements: Natural Vietnamese, clear explanations, good formatting.
    
    Strategy:
    - Simple general_qa: Llama-3.1-8B (very cheap)
    - Complex cases (tax_qa, app_plan, app_read): GPT-4o-mini (better quality)
    
    Args:
        state: Current graph state to determine complexity
        
    Returns:
        Model identifier for OpenRouter
    """
    # Check intent to choose appropriate model
    if state:
        intent = state.get("intent", "general_qa")
        user_input = state.get("user_input", "")
        
        # Simple general_qa can use cheaper model
        if intent == "general_qa" and len(user_input) < 200:
            model = settings.llm_model_answer_simple or "meta-llama/llama-3.1-8b-instruct"
            logger.debug(f"Using simple model for answer (general_qa): {model}")
            return model
        
        # Complex cases need better model
        if intent in ["tax_qa", "app_plan", "app_read"]:
            model = settings.llm_model_answer or "openai/gpt-4o-mini-2024-07-18"
            logger.debug(f"Using advanced model for answer ({intent}): {model}")
            return model
    
    # Default: use GPT-4o-mini for quality answers
    model = settings.llm_model_answer or "openai/gpt-4o-mini-2024-07-18"
    logger.debug(f"Answer model (default): {model}")
    return model


def get_model_for_node(node_name: str, state: Optional[Dict[str, Any]] = None) -> str:
    """
    Get appropriate model for a specific node.
    
    Args:
        node_name: Name of the node ("intent_router", "app_plan", "answer")
        state: Current graph state (optional, for dynamic selection)
        
    Returns:
        Model identifier for OpenRouter
    """
    if node_name == "intent_router":
        return get_model_for_intent_router(state)
    elif node_name == "app_plan":
        return get_model_for_app_plan(state)
    elif node_name == "answer":
        return get_model_for_answer(state)
    else:
        # Fallback to default model
        logger.warning(f"Unknown node name: {node_name}, using default model")
        return settings.llm_model

