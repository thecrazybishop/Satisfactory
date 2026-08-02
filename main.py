import os

from app.gui import MainWindow
from app.poller import Poller, SharedState
from frm import FRMClient


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

    token = os.environ.get("FRM_TOKEN")
    host = os.environ.get("FRM_HOST", "localhost")
    port = int(os.environ.get("FRM_PORT", 8080))

    client = FRMClient(host=host, port=port, token=token)
    state = SharedState()
    poller = Poller(client, state)
    poller.start()

    window = MainWindow(state, poller)
    window.mainloop()


if __name__ == "__main__":
    main()

