import hashlib
import os

# This gets the directory where auth.py is actually sitting
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# This creates a 'data' folder inside that same directory
DATA_DIR = os.path.join(BASE_DIR, "data")
MASTER_HASH_FILE = os.path.join(DATA_DIR, "master.hash")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def master_exists() -> bool:
    return os.path.exists(MASTER_HASH_FILE)

def create_master(password: str):
    # This creates the 'data' folder if it doesn't exist
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    hashed = hash_password(password)
    with open(MASTER_HASH_FILE, "w") as f:
        f.write(hashed)

def verify_master(password: str) -> bool:
    if not master_exists():
        return False

    with open(MASTER_HASH_FILE, "r") as f:
        stored_hash = f.read().strip() # Added .strip() to ignore extra spaces

    return hash_password(password) == stored_hash