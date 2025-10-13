from datetime import datetime

from pydantic import BaseModel


class Api(BaseModel):
    host: str
    version: str = "vNext"
    token: str | None = None
    body: dict = {}

class Auth(BaseModel):
    host: str
    realm: str
    username: str
    password: str
    client_id: str
    client_secret: str

class Token(BaseModel):
    access_token: str
    access_exp: datetime
    refresh_token: str
    refresh_exp: datetime