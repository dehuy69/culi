"""API schemas."""
from app.schemas.common import PaginationParams, PaginationResponse, ErrorResponse
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, ChangePasswordRequest
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceOut
from app.schemas.chat import ChatRequest, ChatMessage, StreamEvent, ConversationOut, ConversationListResponse
from app.schemas.plan import PlanStep, PlanView, PlanDecisionRequest, PlanExecutionStep
from app.schemas.connected_app import (  # NEW
    ConnectedAppCreate,
    ConnectedAppUpdate,
    ConnectedAppResponse,
    SupportedAppResponse,
    TestConnectionResponse,
)

__all__ = [
    "PaginationParams",
    "PaginationResponse",
    "ErrorResponse",
    "UserRegister",
    "UserLogin",
    "TokenResponse",
    "ChangePasswordRequest",
    "WorkspaceCreate",
    "WorkspaceUpdate",
    "WorkspaceOut",
    "ChatRequest",
    "ChatMessage",
    "StreamEvent",
    "ConversationOut",
    "ConversationListResponse",
    "PlanStep",
    "PlanView",
    "PlanDecisionRequest",
    "PlanExecutionStep",
    # Connected app schemas (NEW)
    "ConnectedAppCreate",
    "ConnectedAppUpdate",
    "ConnectedAppResponse",
    "SupportedAppResponse",
    "TestConnectionResponse",
]
