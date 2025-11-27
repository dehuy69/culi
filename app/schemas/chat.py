"""Chat schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.message import MessageSender


class ChatRequest(BaseModel):
    """Chat request."""
    message: str = Field(..., min_length=1)
    conversation_id: Optional[int] = None


class ChatMessage(BaseModel):
    """Chat message schema."""
    id: int
    conversation_id: int
    sender: MessageSender
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class StreamEvent(BaseModel):
    """Server-Sent Event schema."""
    event: str  # "message", "reasoning", "tool_call", "plan", "step", "error", "done"
    data: Dict[str, Any]


class ConversationOut(BaseModel):
    """Conversation response."""
    id: int
    workspace_id: int
    title: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """List of conversations."""
    conversations: List[ConversationOut]
    total: int

