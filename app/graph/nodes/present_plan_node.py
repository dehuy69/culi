"""Present plan node with checkpoint for user approval."""
from typing import Dict, Any
from app.core.logging import get_logger

logger = get_logger(__name__)


def present_plan_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Present plan to user for approval (creates checkpoint).
    
    This node should interrupt the graph and wait for user decision.
    The checkpoint mechanism will be handled by LangGraph.
    
    Args:
        state: Current graph state with plan
        
    Returns:
        Updated state (waiting for user decision)
    """
    plan = state.get("plan", {})
    
    # Format plan for presentation
    plan_description = plan.get("description", "No description")
    steps = plan.get("steps", [])
    
    presentation = f"""
**Kế hoạch thực thi:**

{plan_description}

**Các bước thực hiện ({len(steps)} bước):**
"""
    
    for i, step in enumerate(steps, 1):
        presentation += f"\n{i}. **{step.get('action', 'Unknown')}** - {step.get('description', 'No description')}"
    
    state["answer"] = presentation
    state["plan_approved"] = False  # Wait for user approval
    
    logger.info(f"Plan presented: {len(steps)} steps, waiting for approval")
    
    return state

