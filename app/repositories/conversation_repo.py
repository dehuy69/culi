"""Conversation repository for database operations."""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.conversation import Conversation


class ConversationRepository:
    """Repository for Conversation model operations."""
    
    @staticmethod
    def get_by_id(db: Session, conversation_id: int) -> Optional[Conversation]:
        """Get conversation by ID."""
        return db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    @staticmethod
    def get_by_workspace(db: Session, workspace_id: int, limit: int = 50, offset: int = 0) -> List[Conversation]:
        """Get conversations by workspace with pagination."""
        return db.query(Conversation).filter(
            Conversation.workspace_id == workspace_id
        ).order_by(Conversation.created_at.desc()).limit(limit).offset(offset).all()
    
    @staticmethod
    def create(db: Session, workspace_id: int, title: Optional[str] = None) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(workspace_id=workspace_id, title=title)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation
    
    @staticmethod
    def update(db: Session, conversation: Conversation, title: Optional[str] = None) -> Conversation:
        """Update conversation."""
        if title is not None:
            conversation.title = title
        db.commit()
        db.refresh(conversation)
        return conversation
    
    @staticmethod
    def delete(db: Session, conversation: Conversation) -> None:
        """Delete conversation."""
        db.delete(conversation)
        db.commit()
    
    @staticmethod
    def belongs_to_workspace(db: Session, conversation_id: int, workspace_id: int) -> bool:
        """Check if conversation belongs to workspace."""
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.workspace_id == workspace_id
        ).first()
        return conversation is not None

