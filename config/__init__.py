import json


def get_config(config_type):
    with open(f"config/{config_type}.json", "r") as f:
        config = json.load(f)
    return config

