from fastapi import APIRouter, Depends, HTTPException, Response, Request
from src.services.auth_service import AuthService
from dependency_injector.wiring import Provide, inject
from src.core.container import Container

router = APIRouter(
    prefix="/me",
    tags=["me"],
)


@router.get("/")
@inject
async def get_me(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = auth_service.verifyAccessToken(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Not authenticated")

        user = auth_service.getUser(payload.id)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")

        return {
            "success": True,
            "data": user,
        }

    except Exception:
        raise HTTPException(status_code=403, detail="Invalid token")
