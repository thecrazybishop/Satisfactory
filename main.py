import json
import os
import requests


def load_env(path=".env", override=False):
    try:
        with open(path, "r", encoding="utf-8") as env_file:
            for raw_line in env_file:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")

                if key and (override or key not in os.environ):
                    os.environ[key] = value
    except FileNotFoundError:

        return


def main():
    load_env()
