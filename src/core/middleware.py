from starlette.middleware.base import BaseHTTPMiddleware
from src.models.auth import TokenData
from src.core.security import Security
from src.core.metadata import PUBLIC_ROUTES
from starlette.responses import JSONResponse


class VerifyTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        url = request.url.path

        if url not in PUBLIC_ROUTES:
            token = request.cookies.get("access_token")

            token_data: TokenData | None = Security.getTokenData(token)

            if token_data is None:
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "message": "Invalid Token"},
                )
                # raise HTTPException(status_code=401, detail="Invalid Token")

            if Security.verify_expiry(token_data):
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "message": "Token Expired"},
                )
                # raise HTTPException(status_code=401, detail="Token Expired")

        response = await call_next(request)
        return response
