"""Database models."""
from app.models.user import User
from app.models.workspace import Workspace
from app.models.mcp_connection import MCPConnection, MCPConnectionStatus, MCPConnectionType
from app.models.app_connection import (
    AppConnection,
    ConnectionType,
    ConnectionStatus,
    SupportedAppType,
    MCPAuthType,
)  # DEPRECATED: kept for backward compatibility
from app.models.connected_app import ConnectedApp
from app.models.conversation import Conversation
from app.models.message import Message, MessageSender
from app.models.agent_run import AgentRun
from app.models.agent_step import AgentStep, StepStatus

__all__ = [
    "User",
    "Workspace",
    "MCPConnection",
    "MCPConnectionStatus",
    "MCPConnectionType",
    "AppConnection",  # DEPRECATED
    "ConnectionType",  # DEPRECATED
    "ConnectionStatus",  # DEPRECATED (conflict with ConnectedApp status)
    "SupportedAppType",  # DEPRECATED
    "MCPAuthType",  # DEPRECATED
    "ConnectedApp",  # NEW
    "Conversation",
    "Message",
    "MessageSender",
    "AgentRun",
    "AgentStep",
    "StepStatus",
]

