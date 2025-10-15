from datetime import datetime

from pydantic import BaseModel


class Api(BaseModel):
    """
    Representation of an external API host 
    """

    host: str
    version: str = "vNext"
    token: str | None = None
    body: dict = {}


class Auth(BaseModel):
    """
    Representation of a OAuth2 auth schema
    """

    host: str
    aux_host: str
    realm: str
    username: str
    password: str
    client_id: str
    client_secret: str


class Token(BaseModel):
    """
    Representation of a Bearer Token with refresh
    """

    access_token: str
    access_exp: datetime
    refresh_token: str
    refresh_exp: datetime
