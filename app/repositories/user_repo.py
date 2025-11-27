"""User repository for database operations."""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User


class UserRepository:
    """Repository for User model operations."""
    
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def create(db: Session, username: str, password_hash: str) -> User:
        """Create a new user."""
        user = User(username=username, password_hash=password_hash)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def update_password(db: Session, user: User, password_hash: str) -> User:
        """Update user password."""
        user.password_hash = password_hash
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def exists(db: Session, username: str) -> bool:
        """Check if username exists."""
        return db.query(User).filter(User.username == username).first() is not None

