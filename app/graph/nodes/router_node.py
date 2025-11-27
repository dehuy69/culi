"""Router node for intent classification."""
from typing import Dict, Any
import json
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from app.core.llm_config import get_llm
from app.core.logging import get_logger
from pathlib import Path

logger = get_logger(__name__)


class IntentClassification(BaseModel):
    """Intent classification result."""
    intent: str = Field(description="Classification: small_talk, faq, mcp_read, mcp_plan, web_research")
    reasoning: str = Field(description="Brief explanation")
    needs_web: bool
    needs_mcp: bool
    needs_plan: bool


def router_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Route user input to appropriate processing path.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with intent classification
    """
    user_input = state.get("user_input", "")
    messages = state.get("messages", [])
    mcp_connection = state.get("mcp_connection")
    
    # Load prompt template
    prompt_path = Path(__file__).parent.parent.parent / "prompts" / "router_prompt.txt"
    prompt_template = prompt_path.read_text()
    
    # Build context from messages
    chat_context = "\n".join([
        f"{msg.get('role', 'user')}: {msg.get('content', '')}"
        for msg in messages[-5:]  # Last 5 messages
    ]) if messages else "No previous conversation."
    
    # Format prompt
    prompt = prompt_template.format(
        user_input=user_input,
        chat_context=chat_context,
        mcp_available=str(mcp_connection is not None)
    )
    
    # Get LLM response with structured output
    llm = get_llm(temperature=0.1)
    
    try:
        # Request JSON format
        response = llm.invoke([
            {"role": "system", "content": "You are an intent classifier. Respond only with valid JSON."},
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
        
        classification = json.loads(content)
        
        # Update state
        state["intent"] = classification.get("intent", "faq")
        state["needs_web"] = classification.get("needs_web", False)
        state["needs_mcp"] = classification.get("needs_mcp", False)
        state["needs_plan"] = classification.get("needs_plan", False)
        
        logger.info(f"Intent classified: {state['intent']} (needs_web={state['needs_web']}, needs_mcp={state['needs_mcp']}, needs_plan={state['needs_plan']})")
        
    except Exception as e:
        logger.error(f"Error in router_node: {str(e)}")
        # Default to FAQ on error
        state["intent"] = "faq"
        state["needs_web"] = False
        state["needs_mcp"] = False
        state["needs_plan"] = False
    
    return state

