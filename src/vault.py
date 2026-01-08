import json
import os
from cryptography.fernet import Fernet

# 1. Get the correct directory (the project root)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
VAULT_FILE = os.path.join(DATA_DIR, "vault.enc")


def save_vault(data: dict, fernet: Fernet):
    """Encrypts and saves the vault data to disk."""
    # Ensure the data directory exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    encrypted = fernet.encrypt(json.dumps(data).encode())

    with open(VAULT_FILE, "wb") as f:
        f.write(encrypted)


def load_vault(fernet: Fernet) -> dict:
    """Loads and decrypts the vault data from disk."""
    if not os.path.exists(VAULT_FILE):
        return {}

    with open(VAULT_FILE, "rb") as f:
        encrypted = f.read()

    try:
        decrypted = fernet.decrypt(encrypted)
        return json.loads(decrypted.decode())
    except Exception as e:
        print(f"Decryption error: {e}")
        return {}

