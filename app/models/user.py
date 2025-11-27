"""User model."""
from sqlalchemy import Column, String, DateTime
from datetime import datetime
from app.db.base import BaseModel


class User(BaseModel):
    """User model for authentication."""
    
    __tablename__ = "users"
    
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

