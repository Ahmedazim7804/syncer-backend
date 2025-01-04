from datetime import datetime, timedelta, timezone
import jwt
import os

from envs import ALGORITHM, ACCESS_TOKEN_EXPIRE_HOURS, REFRESH_TOKEN_EXPIRE_HOURS, SECRET_KEY


class Authentication:

    def create_access_token(expires_delta: timedelta | None = None):
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        info = {"exp": expire}

        encoded_jwt = jwt.encode(info, SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt

    def create_refresh_token():
        expire = datetime.now(timezone.utc) + timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS)

        info = {"exp": expire}

        encoded_jwt = jwt.encode(info, SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt

