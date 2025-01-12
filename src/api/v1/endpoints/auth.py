from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from src.models.auth import Token
from src.core.config import Config
from src.services.auth_service import AuthService
from dependency_injector.wiring import Provide, inject
from src.core.container import Container

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/login")
@inject
async def get_access_token_with_password(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], auth_service: AuthService = Depends(Provide[Container.auth_service])) -> Token:


    auth_service.verifyUsernameAndPassword(username=form_data.username, password=form_data.password)
    print(form_data.username)
    refresh_token, access_token = auth_service.createAccessAndRefreshToken(username=form_data.username);

    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="strict", max_age=Config.REFRESH_TOKEN_EXPIRE_HOURS * 60 * 60)
    return Token(access_token=access_token, token_type="bearer")


@router.post("/refresh")
@inject
async def get_access_token_with_refresh_token(request: Request, response: Response, auth_service: AuthService = Depends(Provide[Container.auth_service]) ) -> Token:

    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is missing")

    new_refresh_token, new_access_token = auth_service.refreshAccessToken(refresh_token)

    response.set_cookie(key="refresh_token", value=new_refresh_token, httponly=True, secure=True, samesite="strict", max_age=Config.REFRESH_TOKEN_EXPIRE_HOURS * 60 * 60)
    return Token(access_token=new_access_token, token_type="bearer")
