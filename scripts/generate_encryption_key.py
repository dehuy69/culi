#!/usr/bin/env python3
"""Generate encryption key for MCP client_secret."""
from cryptography.fernet import Fernet

if __name__ == "__main__":
    key = Fernet.generate_key()
    print(f"Encryption key: {key.decode()}")
    print("\nAdd this to your .env file as ENCRYPTION_KEY=")

