from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from src.core.config import Config
from src.services.auth_service import AuthService
from dependency_injector.wiring import Provide, inject
from src.core.container import Container
from src.models.auth import UserLoginForm

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/login")
@inject
async def get_access_token_with_password(
    response: Response,
    body: UserLoginForm,
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
) -> dict:
    auth_service.verifyPassword(password=body.password)
    client = auth_service.createUser(device=body.device)
    refresh_token, access_token = auth_service.createAccessAndRefreshToken(
        id=client.id, device=client.device
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=False,
        secure=False,
        samesite="none",
        max_age=Config.ACCESS_TOKEN_EXPIRE_HOURS * 60 * 60,
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=False,
        secure=False,
        samesite="none",
        max_age=Config.REFRESH_TOKEN_EXPIRE_HOURS * 60 * 60,
        path="/",
    )

    return {
        "success": True,
        "message": "Login successful",
    }


@router.post("/refresh")
@inject
async def get_access_token_with_refresh_token(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
) -> dict:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is missing"
        )

    new_refresh_token, new_access_token = auth_service.refreshAccessToken(refresh_token)

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=Config.ACCESS_TOKEN_EXPIRE_HOURS * 60 * 60,
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=Config.REFRESH_TOKEN_EXPIRE_HOURS * 60 * 60,
        path="/",
    )
    return {
        "success": True,
        "message": "Refresh token successful",
    }
