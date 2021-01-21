import json
import os

os.chdir("/Users/Valeriya/Desktop/Dalberg/spph-email-report/")


def get_config(config_type):
    with open(f"config/{config_type}.json", "r") as f:
        config = json.load(f)
    return config
