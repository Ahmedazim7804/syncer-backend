from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from .platforms import Platform

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: str | None = None
    device: str | None = None
    exp: int | None = None


class UserLoginForm(BaseModel):
    id: str
    device: str
    ip: str
    password: str
    platform: Platform