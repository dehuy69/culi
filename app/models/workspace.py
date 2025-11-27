"""Workspace model."""
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import BaseModel


class Workspace(BaseModel):
    """Workspace model for multi-tenant isolation."""
    
    __tablename__ = "workspaces"
    
    name = Column(String(200), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Relationships
    owner = relationship("User", backref="workspaces")
    
    def __repr__(self):
        return f"<Workspace(id={self.id}, name={self.name}, owner_id={self.owner_id})>"

