from cryptography.fernet import Fernet
import os
import base64
import hashlib


def generate_key(master_password: str) -> bytes:
    """
    Derive encryption key from master password
    """
    hashed = hashlib.sha256(master_password.encode()).digest()
    return base64.urlsafe_b64encode(hashed)
