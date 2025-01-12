from fastapi import HTTPException, status
from src.core.config import Config
from src.core.security import Security
from src.repository import AuthRepository

class AuthService():
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository
    
    def verifyUsernameAndPassword(self, username: str | None, password: str | None):

        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Empty Username", headers={"WWW-Authenticate": "Bearer"})

        if password is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Empty Password", headers={"WWW-Authenticate": "Bearer"})

        if username not in ["mobile", "linux"]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username", headers={"WWW-Authenticate": "Bearer"})

        if password != Config.PASSWORD:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password", headers={"WWW-Authenticate": "Bearer"})

    def verifyRefreshToken(self, refresh_token: str) -> bool:

        if not self.auth_repository.refreshTokenExists(refresh_token):
            return False
        
        token_data = Security.getTokenData(refresh_token)


        if (token_data is None):
            return False
        
        expired = Security.verify_expiry(token_data)

        if expired:
            return False
        
        return True

    def createAccessAndRefreshToken(self, username: str) -> tuple[str, str]:

        access_token = Security.create_access_token(username)
        refresh_token = Security.create_refresh_token(username)

        self.auth_repository.addRefreshToken(refresh_token, username)
    
        return refresh_token, access_token
    
    def refreshAccessToken(self, refresh_token: str) -> tuple[str, str]:
        
        refresh_token_ok = self.verifyRefreshToken(refresh_token)
        
        if not refresh_token_ok:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or Expired refresh token")

        token_data = Security.getTokenData(refresh_token)

        self.auth_repository.removeRefreshToken(refresh_token)
        
        return self.createAccessAndRefreshToken(token_data.role)
        