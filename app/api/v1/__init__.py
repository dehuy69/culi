"""API v1 routers."""
from app.api.v1 import auth_router
from app.api.v1 import health_router
from app.api.v1 import workspace_router
from app.api.v1 import chat_router
from app.api.v1 import mcp_router  # DEPRECATED
from app.api.v1 import app_connection_router  # DEPRECATED
from app.api.v1 import connected_app_router  # NEW

__all__ = [
    "auth_router",
    "health_router",
    "workspace_router",
    "chat_router",
    "mcp_router",
    "app_connection_router",
    "connected_app_router",
]

