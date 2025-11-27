"""Planner node for generating execution plans."""
from typing import Dict, Any
from pathlib import Path
from app.core.llm_config import get_llm
from app.core.logging import get_logger
import json

logger = get_logger(__name__)


def planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate execution plan for complex requests.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with plan
    """
    user_input = state.get("user_input", "")
    chat_context = state.get("chat_context", "")
    accounting_mode = state.get("accounting_mode", "ho_kinh_doanh_don_gian")
    mcp_data = state.get("mcp_data", {})
    
    # Load prompt template
    prompt_path = Path(__file__).parent.parent.parent / "prompts" / "planner_prompt.txt"
    prompt_template = prompt_path.read_text()
    
    # Format prompt
    mcp_data_str = json.dumps(mcp_data, indent=2, ensure_ascii=False) if mcp_data else "None"
    
    prompt = prompt_template.format(
        user_input=user_input,
        chat_context=chat_context,
        accounting_mode=accounting_mode,
        mcp_data=mcp_data_str,
    )
    
    # Get LLM response with structured output
    llm = get_llm(temperature=0.3)
    
    try:
        response = llm.invoke([
            {"role": "system", "content": "You are a planning assistant. Return only valid JSON, no additional text."},
            {"role": "user", "content": prompt + "\n\nReturn only valid JSON, no additional text."}
        ])
        
        # Parse response
        content = response.content.strip()
        # Remove markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        
        plan = json.loads(content)
        
        # Initialize execution state
        state["plan"] = plan
        state["plan_approved"] = False
        state["current_step_index"] = 0
        state["step_results"] = []
        
        logger.info(f"Plan generated: {len(plan.get('steps', []))} steps")
        
    except Exception as e:
        logger.error(f"Error in planner_node: {str(e)}")
        state["error"] = f"Failed to generate plan: {str(e)}"
    
    return state

