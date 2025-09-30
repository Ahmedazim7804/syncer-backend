from fastapi import HTTPException, status
from src.core.config import Config
from src.core.security import Security
from src.repository import AuthRepository
from src.models.client import Client
from src.core.security import TokenData
from src.models.auth import UserLoginForm
from typing import Optional
from datetime import datetime

class AuthService:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    def verifyPassword(self, password: str | None) -> bool:
        if password is None:
            return False

        if password != Config.PASSWORD:
            return False

        return True

    def createUser(self, loginForm: UserLoginForm) -> Client:
        return self.auth_repository.createUser(
            ip=loginForm.ip,
            id=loginForm.id,
            platform=loginForm.platform.value,
            device=loginForm.device,
        )

    def getUser(self, id: str) -> Client:
        return self.auth_repository.getUser(id)

    def verifyAccessToken(self, access_token: str) -> TokenData | None:
        token_data = Security.getTokenData(access_token)

        if token_data is None:
            return None

        expired = Security.verify_expiry(token_data)

        if expired:
            return None

        return token_data

    def verifyRefreshToken(self, refresh_token: str) -> bool:
        if not self.auth_repository.refreshTokenExists(refresh_token):
            return False

        token_data = Security.getTokenData(refresh_token)

        if token_data is None:
            return False

        expired = Security.verify_expiry(token_data)

        if expired:
            return False

        return True

    def createAccessAndRefreshToken(self, id: int, device: str) -> tuple[str, str]:
        access_token = Security.create_access_token(id, device)
        refresh_token = Security.create_refresh_token(id, device)

        self.auth_repository.addRefreshToken(refresh_token, id)

        return refresh_token, access_token

    def refreshAccessToken(self, refresh_token: str) -> tuple[str, str]:
        refresh_token_ok = self.verifyRefreshToken(refresh_token)

        if not refresh_token_ok:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or Expired refresh token",
            )

        token_data = Security.getTokenData(refresh_token)

        self.auth_repository.removeRefreshToken(refresh_token)

        return self.createAccessAndRefreshToken(token_data.id, token_data.device)

    def updateUser(self, id: str, device: Optional[str] = None, ip: Optional[str] = None, last_seen: Optional[datetime] = None):
        self.auth_repository.updateUser(id, ip, device, last_seen);

    def getAllUsers(self):
        return self.auth_repository.getAllUsers()