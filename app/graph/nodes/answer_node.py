"""Answer node for generating final response."""
from typing import Dict, Any
from pathlib import Path
from app.core.llm_config import get_llm
from app.core.logging import get_logger
import json

logger = get_logger(__name__)


def answer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate final answer from all context.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with answer
    """
    user_input = state.get("user_input", "")
    chat_context = state.get("chat_context", "")
    kb_context = state.get("kb_context", "")
    app_data = state.get("app_data", {})
    # Keep backward compatibility with mcp_data
    mcp_data = state.get("mcp_data", {})
    # Use app_data if available, fallback to mcp_data
    data_to_use = app_data if app_data else mcp_data
    web_results = state.get("web_results", [])
    step_results = state.get("step_results", [])
    plan = state.get("plan", {})
    
    # Load prompt template
    prompt_path = Path(__file__).parent.parent.parent / "prompts" / "answer_prompt.txt"
    prompt_template = prompt_path.read_text()
    
    # Format data for prompt - limit size to avoid token limit
    if data_to_use:
        # Limit app_data size to avoid exceeding token limits
        if isinstance(data_to_use, dict):
            # If data has a list, limit it to first 5 items
            limited_data = {}
            for key, value in data_to_use.items():
                if isinstance(value, list) and len(value) > 5:
                    limited_data[key] = value[:5] + [f"... (and {len(value) - 5} more items)"]
                else:
                    limited_data[key] = value
            app_data_str = json.dumps(limited_data, indent=2, ensure_ascii=False)
        else:
            app_data_str = json.dumps(data_to_use, indent=2, ensure_ascii=False)
        # Truncate if still too long
        if len(app_data_str) > 3000:
            app_data_str = app_data_str[:3000] + "... (truncated)"
    else:
        app_data_str = "None"
    web_results_str = json.dumps(web_results, indent=2, ensure_ascii=False) if web_results else "None"
    step_results_str = json.dumps(step_results, indent=2, ensure_ascii=False) if step_results else "None"
    plan_str = json.dumps(plan, indent=2, ensure_ascii=False) if plan else "None"
    
    # Format prompt - use app_data variable name, but accept mcp_data for backward compatibility
    # Replace {mcp_data} with {app_data} if present, or use app_data_str
    formatted_prompt = prompt_template.replace("{mcp_data}", "{app_data}")
    prompt = formatted_prompt.format(
        user_input=user_input,
        chat_context=chat_context,
        kb_context=kb_context,
        app_data=app_data_str,  # Use app_data
        mcp_data=app_data_str,  # Keep for backward compatibility
        web_results=web_results_str,
        step_results=step_results_str,
        plan=plan_str,
    )
    
    # Get LLM response - use optimized model for answer generation
    from app.core.llm_router import get_model_for_answer
    from app.core.config import settings
    model = get_model_for_answer(state)
    llm = get_llm(
        temperature=0.7,
        model=model,
        max_tokens=settings.llm_max_tokens_answer
    )
    
    try:
        response = llm.invoke([
            {"role": "system", "content": "You are Culi, a helpful AI accounting assistant for Vietnamese small businesses. Respond in Vietnamese."},
            {"role": "user", "content": prompt}
        ])
        
        answer = response.content.strip()
        state["answer"] = answer
        
        logger.info("Answer generated successfully")
        
    except Exception as e:
        logger.error(f"Error generating answer: {str(e)}")
        state["answer"] = f"Xin lỗi, đã có lỗi khi tạo phản hồi: {str(e)}"
    
    return state

