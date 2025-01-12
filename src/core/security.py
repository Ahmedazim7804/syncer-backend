import time
import jwt
from datetime import datetime, timezone, timedelta  
from src.models.auth import TokenData
from src.core.config import Config
from fastapi import HTTPException, status

class Security:

    def create_access_token(role: str, expires_delta: timedelta | None = None,):
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(hours=Config.ACCESS_TOKEN_EXPIRE_HOURS)
        info = {"exp": expire, "role": role}

        encoded_jwt = jwt.encode(info, Config.SECRET_KEY, algorithm=Config.ALGORITHM)

        return encoded_jwt

    def create_refresh_token(role: str):
        expire = datetime.now(timezone.utc) + timedelta(hours=Config.REFRESH_TOKEN_EXPIRE_HOURS)

        info = {"exp": expire, "role": role}

        encoded_jwt = jwt.encode(info, Config.SECRET_KEY, algorithm=Config.ALGORITHM)

        return encoded_jwt

    def getTokenData(token: str) -> TokenData | None:
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
            return TokenData(**payload)
        except:
            return None
    
    def verify_expiry(token: TokenData) -> bool:
        try:
            return token.exp < time.time()
        except:
            return False