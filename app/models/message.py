"""Message model."""
from sqlalchemy import Column, String, Integer, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.db.base import BaseModel


class MessageSender(str, enum.Enum):
    """Message sender type."""
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    """Message model for chat messages."""
    
    __tablename__ = "messages"
    
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    sender = Column(SQLEnum(MessageSender), nullable=False)
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, nullable=True)  # Additional metadata (tool calls, reasoning, etc.)
    
    # Relationships
    conversation = relationship("Conversation", backref="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, conversation_id={self.conversation_id}, sender={self.sender})>"

