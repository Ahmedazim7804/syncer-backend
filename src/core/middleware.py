from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import HTTPException
from src.models.auth import oauth2_scheme, TokenData
from src.core.security import Security 
from src.core.metadata import PUBLIC_ROUTES 


class VerifyTokenMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        url = request.url.path

        if url not in PUBLIC_ROUTES:

            token = await oauth2_scheme(request)

            token_data : TokenData | None = Security.getTokenData(token)

            if (token_data is None):
                raise HTTPException(status_code=401, detail="Invalid Token")

            if (Security.verify_expiry(token_data)):
                raise HTTPException(status_code=401, detail="Token Expired")
        
        response = await call_next(request)
        return response