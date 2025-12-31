import json
import os
from cryptography.fernet import Fernet

VAULT_FILE = "data/vault.enc"

def save_vault(data: dict, fernet: Fernet):
    """Encrypts and saves the vault data to disk."""
    encrypted = fernet.encrypt(json.dumps(data).encode())

    if not os.path.exists("data"):
        os.makedirs("data")

    with open(VAULT_FILE, "wb") as f:
        f.write(encrypted)

def load_vault(fernet: Fernet) -> dict:
    """Loads and decrypts the vault data from disk."""
    if not os.path.exists(VAULT_FILE):
        return {}

    with open(VAULT_FILE, "rb") as f:
        encrypted = f.read()

    decrypted = fernet.decrypt(encrypted)
    return json.loads(decrypted.decode())

