"""Encryption utilities for sensitive data."""
from cryptography.fernet import Fernet
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Generate key from settings encryption_key (should be 32 bytes base64 encoded)
try:
    # Ensure encryption_key is properly formatted
    key = settings.encryption_key.encode()
    if len(key) < 32:
        # Pad or repeat key to 32 bytes
        key = (key * (32 // len(key) + 1))[:32]
    
    # Base64 encode for Fernet
    import base64
    key = base64.urlsafe_b64encode(key)
    cipher_suite = Fernet(key)
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

