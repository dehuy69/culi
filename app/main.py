"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1 import auth_router, health_router, workspace_router, chat_router, mcp_router, app_connection_router, connected_app_router

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI agent for accounting assistance for Vietnamese small businesses",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(health_router.router, prefix="/api/v1")
app.include_router(workspace_router.router, prefix="/api/v1")
app.include_router(chat_router.router, prefix="/api/v1")
app.include_router(mcp_router.router, prefix="/api/v1")  # DEPRECATED: use connected_app_router
app.include_router(app_connection_router.router, prefix="/api/v1")  # DEPRECATED: use connected_app_router
app.include_router(connected_app_router.router, prefix="/api/v1")  # NEW: connected apps API


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    from app.core.logging import get_logger
    # Import domain apps to register adapters
    from app.domain.apps import *  # noqa: F401, F403
    logger = get_logger(__name__)
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    from app.core.logging import get_logger
    logger = get_logger(__name__)
    logger.info(f"Shutting down {settings.app_name}")

