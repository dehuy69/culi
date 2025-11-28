"""Context node for gathering conversational context."""
from typing import Dict, Any
from app.core.logging import get_logger

logger = get_logger(__name__)


def context_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Gather conversational context from chat history.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with chat_context
    """
    messages = state.get("messages", [])
    intent = state.get("intent", "general_qa")
    
    # Summarize recent messages (simple concatenation for now)
    # TODO: Use LangChain memory for better summarization
    from app.core.config import settings
    history_length = settings.chat_history_length
    
    if messages:
        recent_messages = messages[-history_length:]  # Use configurable history length
        chat_context = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in recent_messages
        ])
    else:
        chat_context = "No previous conversation."
    
    state["chat_context"] = chat_context
    state["kb_context"] = ""  # Placeholder for future RAG
    
    logger.debug(f"Context gathered: {len(messages)} messages, intent: {intent}")
    return state

