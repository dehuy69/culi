"""Graph nodes."""
from app.graph.nodes.router_node import router_node  # DEPRECATED: use intent_router_node
from app.graph.nodes.intent_router_node import intent_router_node  # NEW
from app.graph.nodes.context_node import context_node
from app.graph.nodes.web_search_node import web_search_node
from app.graph.nodes.mcp_read_node import mcp_read_node  # DEPRECATED
from app.graph.nodes.app_read_node import app_read_node_sync as app_read_node  # NEW: generic app read
from app.graph.nodes.planner_node import planner_node  # DEPRECATED: use app_plan_node
from app.graph.nodes.app_plan_node import app_plan_node  # NEW: generic app plan
from app.graph.nodes.present_plan_node import present_plan_node
from app.graph.nodes.execute_plan_node import execute_plan_node
from app.graph.nodes.answer_node import answer_node
from app.graph.nodes.error_node import error_node

__all__ = [
    "router_node",  # DEPRECATED
    "intent_router_node",  # NEW
    "context_node",
    "web_search_node",
    "mcp_read_node",  # DEPRECATED
    "app_read_node",  # NEW
    "planner_node",  # DEPRECATED
    "app_plan_node",  # NEW
    "present_plan_node",
    "execute_plan_node",
    "answer_node",
    "error_node",
]

