"""LangGraph application graph setup."""
from langgraph.graph import StateGraph, END
from typing import Literal
from app.graph.state import CuliState
from app.graph.nodes import (
    context_node,
    web_search_node,
    present_plan_node,
    execute_plan_node,
    answer_node,
    error_node,
)
from app.graph.nodes.intent_router_node import intent_router_node
from app.graph.nodes.app_read_node import app_read_node_sync as app_read_node
from app.graph.nodes.app_plan_node import app_plan_node
from app.core.logging import get_logger

logger = get_logger(__name__)


def route_intent(state: CuliState) -> Literal["general_qa", "tax_qa", "app_read", "app_plan", "no_app", "web_research"]:
    """Route based on intent."""
    intent = state.get("intent", "general_qa")
    
    # Map new intents
    if intent == "general_qa":
        return "general_qa"
    elif intent == "tax_qa":
        return "tax_qa"
    elif intent == "app_read":
        return "app_read"
    elif intent == "app_plan":
        return "app_plan"
    elif intent == "no_app":
        return "no_app"
    elif intent == "web_research":  # Keep for backward compatibility
        return "web_research"
    else:
        # Backward compatibility with old intents
        if intent in ["mcp_read", "faq"]:
            return "general_qa"
        return "general_qa"


def route_plan_approval(state: CuliState) -> Literal["execute", "cancel"]:
    """Route based on plan approval."""
    if state.get("plan_approved", False):
        return "execute"
    else:
        return "cancel"


def should_continue_execution(state: CuliState) -> Literal["continue", "finish"]:
    """Check if plan execution should continue."""
    plan = state.get("plan", {})
    steps = plan.get("steps", [])
    current_step_index = state.get("current_step_index", 0)
    
    if current_step_index >= len(steps):
        return "finish"
    return "continue"


def route_after_context(state: CuliState) -> Literal["answer", "app_read", "app_plan"]:
    """Route after context node based on intent."""
    intent = state.get("intent", "general_qa")
    
    if intent == "general_qa":
        return "answer"
    elif intent == "app_read":
        return "app_read"
    elif intent == "app_plan":
        return "app_plan"
    else:
        return "answer"


def build_graph() -> StateGraph:
    """Build and return the LangGraph application."""
    # Create graph
    workflow = StateGraph(CuliState)
    
    # Add nodes
    workflow.add_node("intent_router", intent_router_node)  # New intent router
    workflow.add_node("context", context_node)
    workflow.add_node("web_search", web_search_node)  # Use Google Custom Search API
    workflow.add_node("app_read", app_read_node)  # Generic app read node
    workflow.add_node("app_plan", app_plan_node)  # New app plan node
    workflow.add_node("present_plan", present_plan_node)
    workflow.add_node("execute_plan", execute_plan_node)
    workflow.add_node("answer", answer_node)
    workflow.add_node("error", error_node)
    
    # Keep deprecated nodes for backward compatibility (optional)
    # workflow.add_node("router", router_node)  # DEPRECATED
    # workflow.add_node("mcp_read", mcp_read_node)  # DEPRECATED
    # workflow.add_node("planner", planner_node)  # DEPRECATED
    
    # Set entry point - use new intent_router
    workflow.set_entry_point("intent_router")
    
    # Add routing edges - new intent system
    workflow.add_conditional_edges(
        "intent_router",
        route_intent,
        {
            "general_qa": "context",
            "tax_qa": "web_search",
            "app_read": "context",
            "app_plan": "context",
            "no_app": "answer",  # Direct to answer if no app
            "web_research": "web_search",  # Backward compatibility
        }
    )
    
    # Context routing - new system
    workflow.add_conditional_edges(
        "context",
        route_after_context,
        {
            "answer": "answer",
            "app_read": "app_read",
            "app_plan": "app_plan",
        }
    )
    
    # After web search -> answer
    workflow.add_edge("web_search", "answer")
    
    # After app read -> answer
    workflow.add_edge("app_read", "answer")
    
    # After app_plan -> present plan
    workflow.add_edge("app_plan", "present_plan")
    
    # Plan approval routing (simplified - in production use checkpoints)
    workflow.add_conditional_edges(
        "present_plan",
        route_plan_approval,
        {
            "execute": "execute_plan",
            "cancel": "answer",
        }
    )
    
    # Plan execution loop
    workflow.add_conditional_edges(
        "execute_plan",
        should_continue_execution,
        {
            "continue": "execute_plan",
            "finish": "answer",
        }
    )
    
    # Error handling (simplified)
    workflow.add_edge("answer", END)
    workflow.add_edge("error", END)
    
    return workflow.compile()


# Global graph instance
_app_graph = None


def get_graph():
    """Get the compiled graph instance."""
    global _app_graph
    if _app_graph is None:
        _app_graph = build_graph()
        logger.info("LangGraph application graph compiled")
    return _app_graph

