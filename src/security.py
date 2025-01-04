from datetime import datetime, timedelta, timezone
import jwt
import os
from models.token import TokenData
from envs import ALGORITHM, ACCESS_TOKEN_EXPIRE_HOURS, REFRESH_TOKEN_EXPIRE_HOURS, SECRET_KEY


class Authentication:

    def create_access_token(role: str, expires_delta: timedelta | None = None,):
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        info = {"exp": expire, "role": role}

        encoded_jwt = jwt.encode(info, SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt

    def create_refresh_token(role: str):
        expire = datetime.now(timezone.utc) + timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS)

        info = {"exp": expire, "role": role}

        encoded_jwt = jwt.encode(info, SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt

    def verify_access_token(token: str | None) -> TokenData | None:
        if token is None:
            return None

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return TokenData(**payload)
        except:
            return None


