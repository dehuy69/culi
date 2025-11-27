"""Security utilities for JWT and password hashing."""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Password hashing context
# Use bcrypt with rounds=12 (default) and handle 72-byte limit
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    # Ensure password is a string
    if isinstance(plain_password, bytes):
        plain_password = plain_password.decode('utf-8')
    password_str = str(plain_password) if plain_password is not None else ""
    
    # Handle bcrypt 72-byte limit for verification
    password_bytes = password_str.encode('utf-8')
    if len(password_bytes) > 72:
        truncated = password_bytes[:72]
        while True:
            try:
                password_str = truncated.decode('utf-8')
                break
            except UnicodeDecodeError:
                if len(truncated) == 0:
                    return False
                truncated = truncated[:-1]
    
    try:
        return pwd_context.verify(password_str, hashed_password)
    except (ValueError, TypeError):
        # Fallback to direct bcrypt if passlib fails
        try:
            import bcrypt
            password_bytes = password_str.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            hashed_bytes = hashed_password.encode('utf-8') if isinstance(hashed_password, str) else hashed_password
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            return False


def get_password_hash(password: str) -> str:
    """Hash a password."""
    # Ensure password is a string (not bytes)
    if isinstance(password, bytes):
        password = password.decode('utf-8')
    
    # Convert to string and ensure it's not None
    password_str = str(password) if password is not None else ""
    
    # Bcrypt has a 72-byte limit, so we need to truncate if necessary
    # But we should warn users if password is too long
    password_bytes = password_str.encode('utf-8')
    if len(password_bytes) > 72:
        # Truncate to 72 bytes, handling UTF-8 encoding properly
        # Remove bytes from the end until we have a valid UTF-8 string
        truncated = password_bytes[:72]
        while True:
            try:
                password_str = truncated.decode('utf-8')
                break
            except UnicodeDecodeError:
                if len(truncated) == 0:
                    raise ValueError("Password cannot be encoded as UTF-8")
                truncated = truncated[:-1]
    
    # Use passlib's hash method - it should handle the password correctly
    try:
        return pwd_context.hash(password_str)
    except ValueError as e:
        # If there's still an error, it might be a passlib/bcrypt version issue
        # Try with a simpler approach
        import bcrypt
        password_bytes = password_str.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT access token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None

