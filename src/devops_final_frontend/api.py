from datetime import datetime, timedelta

import httpx

from devops_final_frontend.models import Api, Auth, Token


class ApiService:
    """
    Utility Class that encapsulates api calls into service operations  
    """

    @staticmethod
    def is_api_up(params: Api) -> bool:
        """
        Check if the LLM API is available by calling the root endpoint.
        If connection cannot be established consider the api down 
        """
        with httpx.Client(follow_redirects=True) as client:
            try:
                client.get(f"{params.host}/")
                return True
            except httpx.HTTPError:
                return False

    @staticmethod
    def is_keycloak_up(params: Auth):
        """
        Check if the Keycloack Instance is available by calling the root endpoint.
        If connection cannot be established consider the api down 
        """
        with httpx.Client() as client:
            try:
                client.get(f"{params.host}/health/ready", timeout=2)
                return True
            except httpx.HTTPError:
                return False

    @staticmethod
    def get_compose_get(params: Api) -> dict:
        """
        Invoke the LLM Compose generation Endpoint
        """

        raw_values = params.body
        params.body = {}
        params.token = raw_values["auth"]["access_token"]
        params.body["services"] = raw_values["services"]
        params.body["project"] = "TODO"
        params.body["network_name"] = raw_values["network"]["name"]
        params.body["network_exists"] = raw_values["network"]["exists"]
        params.body["volume_mount"] = raw_values["volume_mount"]

        with httpx.Client(follow_redirects=True, timeout=180) as client:
            r = client.post(
                f"{params.host}/{params.version}/gen/compose",
                json=params.body,
                headers={"Authorization": f"Bearer {params.token}"},
            )

            r.raise_for_status()
            return r.json()

    @staticmethod
    def get_token(params: Auth) -> Token:
        """
        Authenticate the streamlit app with the backend keycloak instance
        """

        with httpx.Client() as client:
            r = client.post(
                f"{params.host}/realms/{params.realm}/protocol/openid-connect/token",
                data={
                    "grant_type": "password",
                    "username": params.username,
                    "password": params.password,
                    "client_id": params.client_id,
                    "client_secret": params.client_secret,
                },
            )

            r.raise_for_status()
            data = r.json()
            return Token(
                access_token=data["access_token"],
                access_exp=datetime.now() + timedelta(seconds=data["expires_in"]),
                refresh_token=data["refresh_token"],
                refresh_exp=datetime.now() + timedelta(seconds=data["refresh_expires_in"]),
            )

    @staticmethod
    def refresh_token(params: Auth, refresh_token: str):
        """
        Refresh the app's token with the backend keycloak instance
        """

        with httpx.Client() as client:
            r = client.post(
                f"{params.host}/realms/{params.realm}/protocol/openid-connect/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": params.client_id,
                    "client_secret": params.client_secret,
                },
            )

            r.raise_for_status()
            data = r.json()
            return Token(
                access_token=data["access_token"],
                access_exp=datetime.now() + timedelta(seconds=data["expires_in"]),
                refresh_token=data["refresh_token"],
                refresh_exp=datetime.now() + timedelta(seconds=data["refresh_expires_in"]),
            )
