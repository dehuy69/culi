"""API v1 routers."""
from app.api.v1 import auth_router
from app.api.v1 import health_router
from app.api.v1 import workspace_router
from app.api.v1 import chat_router
from app.api.v1 import mcp_router  # DEPRECATED: use connected_app_router
from app.api.v1 import connected_app_router

__all__ = [
    "auth_router",
    "health_router",
    "workspace_router",
    "chat_router",
    "mcp_router",
    "connected_app_router",
]

