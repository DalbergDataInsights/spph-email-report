import json


def get_config():
    with open("config/config.json", "r") as f:
        config = json.load(f)
    return config