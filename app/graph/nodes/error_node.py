"""Error handling node."""
from typing import Dict, Any
from app.core.logging import get_logger

logger = get_logger(__name__)


def error_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle errors and generate user-friendly error messages.
    
    Args:
        state: Current graph state with error information
        
    Returns:
        Updated state with error message
    """
    error = state.get("error", "An unexpected error occurred")
    
    # Generate friendly error message
    error_message = f"""
Xin lỗi, đã có lỗi xảy ra:

{error}

Vui lòng thử lại hoặc liên hệ hỗ trợ nếu vấn đề vẫn tiếp tục.
"""
    
    state["answer"] = error_message
    logger.error(f"Error node executed: {error}")
    
    return state

