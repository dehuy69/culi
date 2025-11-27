"""Agent run model for logging LangGraph executions."""
from sqlalchemy import Column, Integer, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import BaseModel


class AgentRun(BaseModel):
    """Agent run log for tracking LangGraph executions."""
    
    __tablename__ = "agent_runs"
    
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    state_before = Column(JSON, nullable=True)  # State snapshot before execution
    state_after = Column(JSON, nullable=True)   # State snapshot after execution
    
    # Relationships
    conversation = relationship("Conversation", backref="agent_runs")
    
    def __repr__(self):
        return f"<AgentRun(id={self.id}, conversation_id={self.conversation_id})>"

