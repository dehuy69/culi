"""App plan node for generating execution plans based on app category."""
from typing import Dict, Any
from pathlib import Path
from app.core.llm_config import get_llm
from app.core.logging import get_logger
import json

logger = get_logger(__name__)


def app_plan_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate execution plan for app operations.
    Strategy differs based on app category:
    - POS_SIMPLE: Focus on creating products, invoices, categories
    - ACCOUNTING: Focus on mapping accounts, journal entries
    - UNKNOWN: Limited operations
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with plan
    """
    user_input = state.get("user_input", "")
    chat_context = state.get("chat_context", "")
    connected_app = state.get("connected_app")
    app_data = state.get("app_data", {})
    
    # Determine app category and strategy
    app_category = "UNKNOWN"
    app_name = "Unknown"
    if connected_app:
        app_category = connected_app.get("category", "UNKNOWN")
        app_name = connected_app.get("name", "Unknown")
    
    # Load prompt template
    prompt_path = Path(__file__).parent.parent.parent / "prompts" / "app_plan_prompt.txt"
    
    # Fallback to old prompt if new one doesn't exist
    if not prompt_path.exists():
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "planner_prompt.txt"
    
    prompt_template = prompt_path.read_text()
    
    # Format prompt
    app_data_str = json.dumps(app_data, indent=2, ensure_ascii=False) if app_data else "None"
    
    prompt = prompt_template.format(
        user_input=user_input,
        chat_context=chat_context,
        app_name=app_name,
        app_category=app_category,
        app_data=app_data_str,
    )
    
    # Get LLM response with structured output
    llm = get_llm(temperature=0.3)
    
    try:
        response = llm.invoke([
            {
                "role": "system",
                "content": "You are a planning assistant. Generate a plan with generic actions (CREATE_PRODUCT, CREATE_INVOICE, etc.). "
                          "Return only valid JSON, no additional text."
            },
            {
                "role": "user",
                "content": prompt + "\n\nReturn only valid JSON, no additional text."
            }
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
        
        # Ensure plan has required structure
        if "steps" not in plan:
            plan["steps"] = []
        if "description" not in plan:
            plan["description"] = "Execution plan"
        
        # Validate step format
        for i, step in enumerate(plan["steps"]):
            if "id" not in step:
                step["id"] = i + 1
            if "action" not in step:
                step["action"] = "UNKNOWN"
            if "params" not in step:
                step["params"] = {}
        
        # Initialize execution state
        state["plan"] = plan
        state["plan_approved"] = False
        state["current_step_index"] = 0
        state["step_results"] = []
        
        logger.info(f"Plan generated for {app_name} ({app_category}): {len(plan.get('steps', []))} steps")
        
    except Exception as e:
        logger.error(f"Error in app_plan_node: {str(e)}", exc_info=True)
        state["error"] = f"Failed to generate plan: {str(e)}"
    
    return state

