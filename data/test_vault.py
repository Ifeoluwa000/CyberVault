from src.crypto_utils import generate_key
from cryptography.fernet import Fernet
from src import vault

master = "TestPassword123"

key = generate_key(master)
fernet = Fernet(key)

data = {
    "gmail": {
        "username": "test@gmail.com",
        "password": "secret123"
    }
}

vault.save_vault(data, fernet)

loaded = vault.load_vault(fernet)
print(loaded)
