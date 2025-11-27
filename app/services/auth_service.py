"""Authentication service."""
from datetime import timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, ChangePasswordRequest
from app.core.logging import get_logger

logger = get_logger(__name__)


class AuthService:
    """Service for authentication operations."""
    
    @staticmethod
    def register(db: Session, user_data: UserRegister) -> User:
        """Register a new user."""
        # Check if username already exists
        if UserRepository.exists(db, user_data.username):
            raise ValueError("Username already exists")
        
        # Ensure password is a string and validate length
        password = str(user_data.password) if user_data.password else ""
        if len(password.encode('utf-8')) > 72:
            raise ValueError("Password is too long (maximum 72 bytes)")
        
        # Hash password
        password_hash = get_password_hash(password)
        
        # Create user
        user = UserRepository.create(db, user_data.username, password_hash)
        logger.info(f"User registered: {user.username}")
        return user
    
    @staticmethod
    def authenticate(db: Session, login_data: UserLogin) -> Optional[TokenResponse]:
        """Authenticate user and return access token."""
        # Get user by username
        user = UserRepository.get_by_username(db, login_data.username)
        if not user:
            return None
        
        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            return None
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=access_token_expires
        )
        
        logger.info(f"User authenticated: {user.username}")
        return TokenResponse(access_token=access_token, token_type="bearer")
    
    @staticmethod
    def change_password(db: Session, user: User, password_data: ChangePasswordRequest) -> User:
        """Change user password."""
        # Verify old password
        if not verify_password(password_data.old_password, user.password_hash):
            raise ValueError("Incorrect old password")
        
        # Hash new password
        new_password_hash = get_password_hash(password_data.new_password)
        
        # Update password
        updated_user = UserRepository.update_password(db, user, new_password_hash)
        logger.info(f"Password changed for user: {user.username}")
        return updated_user

