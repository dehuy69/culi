"""Message repository for database operations."""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.message import Message, MessageSender


class MessageRepository:
    """Repository for Message model operations."""
    
    @staticmethod
    def get_by_id(db: Session, message_id: int) -> Optional[Message]:
        """Get message by ID."""
        return db.query(Message).filter(Message.id == message_id).first()
    
    @staticmethod
    def get_by_conversation(
        db: Session,
        conversation_id: int,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Message]:
        """Get messages by conversation."""
        query = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc())
        
        if limit:
            query = query.limit(limit).offset(offset)
        
        return query.all()
    
    @staticmethod
    def create(
        db: Session,
        conversation_id: int,
        sender: MessageSender,
        content: str,
        metadata: Optional[dict] = None
    ) -> Message:
        """Create a new message."""
        message = Message(
            conversation_id=conversation_id,
            sender=sender,
            content=content,
            message_metadata=metadata
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    
    @staticmethod
    def get_latest(db: Session, conversation_id: int, limit: int = 10) -> List[Message]:
        """Get latest messages from conversation."""
        return db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def delete(db: Session, message: Message) -> None:
        """Delete message."""
        db.delete(message)
        db.commit()

