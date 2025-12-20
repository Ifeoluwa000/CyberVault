import hashlib
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MASTER_HASH_FILE = os.path.join(DATA_DIR, "master.hash")



def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def master_exists() -> bool:
    return os.path.exists(MASTER_HASH_FILE)


def create_master(password: str):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    hashed = hash_password(password)
    with open(MASTER_HASH_FILE, "w") as f:
        f.write(hashed)



def verify_master(password: str) -> bool:
    if not master_exists():
        return False

    with open(MASTER_HASH_FILE, "r") as f:
        stored_hash = f.read()

    return hash_password(password) == stored_hash
