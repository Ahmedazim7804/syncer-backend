from src.models.auth import oauth2_scheme
from fastapi import Depends, HTTPException, status
from typing import Annotated
from src.core.security import Security


class Dependencies:
    @staticmethod
    def get_username(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
        token_data = Security.getTokenData(token)

        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        return token_data.role
