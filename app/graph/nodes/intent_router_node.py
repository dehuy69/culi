"""Intent router node for classifying user intent based on connected app."""
from typing import Dict, Any
import json
from langchain.prompts import ChatPromptTemplate
from app.core.llm_config import get_llm
from app.core.logging import get_logger
from pathlib import Path

logger = get_logger(__name__)


def intent_router_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Route user input to appropriate processing path based on intent and connected app.
    
    Intent values:
    - general_qa: Hỏi chung, không cần app
    - tax_qa: Hỏi về thuế, chế độ kế toán → cần web search
    - app_read: Xem báo cáo, hỏi doanh thu, hỏi hóa đơn → cần đọc từ app
    - app_plan: Yêu cầu setup, chỉnh sửa dữ liệu → cần lập plan + ghi vào app
    - no_app: Chưa cấu hình app mà lại đòi coi số liệu
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with intent classification
    """
    user_input = state.get("user_input", "")
    messages = state.get("messages", [])
    connected_app = state.get("connected_app")
    
    # Load prompt template
    prompt_path = Path(__file__).parent.parent.parent / "prompts" / "intent_router_prompt.txt"
    
    # Fallback to old prompt if new one doesn't exist
    if not prompt_path.exists():
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "router_prompt.txt"
    
    if not prompt_path.exists():
        logger.warning(f"Prompt file not found: {prompt_path}")
        prompt_template = "Classify user intent based on input: {user_input}"
    else:
        prompt_template = prompt_path.read_text()
    
    # Build context from messages
    chat_context = "\n".join([
        f"{msg.get('role', 'user')}: {msg.get('content', '')}"
        for msg in messages[-5:]  # Last 5 messages
    ]) if messages else "No previous conversation."
    
    # Build app context
    app_context = "None"
    if connected_app:
        app_name = connected_app.get("name", "Unknown")
        app_category = connected_app.get("category", "UNKNOWN")
        app_context = f"App: {app_name}, Category: {app_category}"
    
    # Format prompt
    prompt = prompt_template.format(
        user_input=user_input,
        chat_context=chat_context,
        app_context=app_context,
        app_available=str(connected_app is not None)
    )
    
    # Get LLM response
    llm = get_llm(temperature=0.1)
    
    try:
        # Request JSON format
        response = llm.invoke([
            {
                "role": "system",
                "content": "You are an intent classifier. Classify user intent into: general_qa, tax_qa, app_read, app_plan, or no_app. "
                          "Respond only with valid JSON containing: intent, reasoning, needs_web, needs_app, needs_plan."
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
        
        classification = json.loads(content)
        
        # Update state with new intent values
        intent = classification.get("intent", "general_qa")
        
        # Validate intent
        valid_intents = ["general_qa", "tax_qa", "app_read", "app_plan", "no_app"]
        if intent not in valid_intents:
            logger.warning(f"Invalid intent '{intent}', defaulting to 'general_qa'")
            intent = "general_qa"
        
        # Check if no_app should be set (user asks for app data but no app configured)
        if not connected_app and intent in ["app_read", "app_plan"]:
            intent = "no_app"
        
        state["intent"] = intent
        state["needs_web"] = classification.get("needs_web", False) or intent == "tax_qa"
        state["needs_app"] = classification.get("needs_app", False) or intent in ["app_read", "app_plan"]
        state["needs_plan"] = classification.get("needs_plan", False) or intent == "app_plan"
        
        logger.info(
            f"Intent classified: {state['intent']} "
            f"(needs_web={state['needs_web']}, needs_app={state['needs_app']}, needs_plan={state['needs_plan']})"
        )
        
    except Exception as e:
        logger.error(f"Error in intent_router_node: {str(e)}", exc_info=True)
        # Default to general_qa on error
        state["intent"] = "general_qa"
        state["needs_web"] = False
        state["needs_app"] = False
        state["needs_plan"] = False
    
    return state

