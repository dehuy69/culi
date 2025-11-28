"""Encryption utilities for sensitive data."""
from cryptography.fernet import Fernet
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Initialize Fernet with encryption_key from settings
# The key in .env should already be a valid Fernet key (base64-encoded 32 bytes)
try:
    import base64
    key_str = settings.encryption_key.strip().strip('"').strip("'")  # Remove quotes if present
    
    # Try to use the key directly as Fernet key
    try:
        # Validate it's a valid Fernet key by decoding
        base64.urlsafe_b64decode(key_str)
        cipher_suite = Fernet(key_str.encode())
        logger.info("Encryption initialized with key from settings")
    except Exception:
        # If not valid, generate a new key and log warning
        logger.warning(f"Invalid encryption key format. Generating new key. Please update ENCRYPTION_KEY in .env")
        new_key = Fernet.generate_key()
        logger.warning(f"Generated new key: {new_key.decode()}")
        cipher_suite = Fernet(new_key)
except Exception as e:
    logger.warning(f"Failed to initialize encryption: {e}. Using dummy key (DO NOT USE IN PRODUCTION)")
    # Fallback for development - DO NOT USE IN PRODUCTION
    cipher_suite = Fernet(Fernet.generate_key())


def encrypt(plaintext: str) -> str:
    """Encrypt a plaintext string."""
    if not plaintext:
        return ""
    return cipher_suite.encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    """Decrypt a ciphertext string."""
    if not ciphertext:
        return ""
    return cipher_suite.decrypt(ciphertext.encode()).decode()

