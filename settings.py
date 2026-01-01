import json
import os

SETTINGS_FILE = "data/settings.json"


def load_settings():
    # Create folder if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists(SETTINGS_FILE):
        return {"theme": "darkly", "min_length": 8, "require_number": True, "require_upper": True,
                "require_special": True}

    with open(SETTINGS_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {"theme": "darkly", "min_length": 8, "require_number": True, "require_upper": True,
                    "require_special": True}


def save_settings(settings_data):
    if not os.path.exists("data"):
        os.makedirs("data")
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings_data, f, indent=4)