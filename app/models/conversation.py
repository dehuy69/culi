"""Conversation model."""
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import BaseModel


class Conversation(BaseModel):
    """Conversation model for chat sessions."""
    
    __tablename__ = "conversations"
    
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False, index=True)
    title = Column(String(500), nullable=True)  # Auto-generated or user-set title
    
    # Relationships
    workspace = relationship("Workspace", backref="conversations")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, workspace_id={self.workspace_id}, title={self.title})>"

