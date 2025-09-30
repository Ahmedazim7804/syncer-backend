from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from src.services.auth_service import AuthService
from dependency_injector.wiring import Provide, inject
from src.core.container import Container
from src.models.auth import UserLoginForm
from pydantic import BaseModel

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


class AuthResponse(BaseModel):
    success: bool
    access_token: str
    refresh_token: str
    message: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/login")
@inject
async def get_access_token_with_password(
    response: Response,
    body: UserLoginForm,
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
) -> AuthResponse:
    if not auth_service.verifyPassword(password=body.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )

    try:
        client = auth_service.createUser(body)
        refresh_token, access_token = auth_service.createAccessAndRefreshToken(
            id=client.id, device=client.device
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str("Failed to create user"),
        )

    return AuthResponse(
        success=True,
        access_token=access_token,
        refresh_token=refresh_token,
        message="Login successful",
    )


@router.post("/refresh")
@inject
async def get_access_token_with_refresh_token(
    request: Request,
    response: Response,
    body: RefreshTokenRequest,
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
) -> AuthResponse:
    refresh_token = body.refresh_token

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is missing",
        )

    try:
        new_refresh_token, new_access_token = auth_service.refreshAccessToken(
            refresh_token
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str("Failed to refresh access token"),
        )

    return AuthResponse(
        success=True,
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        message="Refresh token successful",
    )
