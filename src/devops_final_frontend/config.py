"""Application Configuration Functionalities"""

import os
from pathlib import Path

import toml
from dotenv import load_dotenv


def create_secrets_file():
    """Load the .env file in os.env put the values from that environment into the secrets.toml file used by streamlit"""

    path = Path(Path(__file__).resolve().parents[2] / ".streamlit/secrets.toml")
    path.parent.mkdir(parents=True, exist_ok=True)

    load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")
    with open(path, "w", encoding="utf-8") as file:
        toml.dump(
            {
                "auth": {
                    "redirect_uri": os.getenv("AUTH_REDIRECT_URI"),
                    "cookie_secret": os.getenv("AUTH_COOKIE_SECRET"),
                    "keycloak": {
                        "client_id": os.getenv("AUTH_KEYCLOAK_CLIENT_ID"),
                        "client_secret": os.getenv("AUTH_KEYCLOAK_CLIENT_SECRET"),
                        "server_metadata_url": os.getenv("AUTH_KEYCLOAK_SERVER_METADATA_URL"),
                        "client_kwargs": {"prompt": os.getenv("AUTH_KEYCLOAK_CLIENT_KWARGS_PROMPT", "login")},
                    },
                },
                "backend": {
                    "host": os.getenv("BACKEND_HOST"),
                    "version": os.getenv("BACKEND_VERSION"),
                    "auth": {
                        "host": os.getenv("BACKEND_AUTH_HOST"),
                        "aux_host": os.getenv("BACKEND_AUTH_AUX_HOST"),
                        "realm": os.getenv("BACKEND_AUTH_REALM"),
                        "username": os.getenv("BACKEND_AUTH_USERNAME"),
                        "password": os.getenv("BACKEND_AUTH_PASSWORD"),
                        "client_id": os.getenv("BACKEND_AUTH_CLIENT_ID"),
                        "client_secret": os.getenv("BACKEND_AUTH_CLIENT_SECRET"),
                    },
                },
            },
            file,
        )
