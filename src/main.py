from typing import Union, Annotated
from pydantic import BaseModel
from fastapi import FastAPI, status, Depends, HTTPException, Response, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from security import Authentication
from database import Database
from models.token import Token, TokenData

from envs import ACCESS_TOKEN_EXPIRE_HOURS, REFRESH_TOKEN_EXPIRE_HOURS

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class Token(BaseModel):
    access_token: str
    token_type: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/login")
async def get_access_token_with_password(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[Database.get_db, Depends()]) -> Token:
    if form_data.username not in ["mobile", "linux"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username", headers={"WWW-Authenticate": "Bearer"})
    
    access_token = Authentication.create_access_token(form_data.username)
    refresh_token = Authentication.create_refresh_token(form_data.username)

    db.addRefreshToken(refresh_token, form_data.username)

    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="strict", max_age=REFRESH_TOKEN_EXPIRE_HOURS * 60 * 60)

    return Token(access_token=access_token, token_type="bearer")


@app.post("/refresh")
async def get_access_token_with_refresh_token(request: Request, response: Response, db: Annotated[Database, Depends(Database.get_db)]) -> Token:

    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is missing")
    
    refresh_token_ok = db.verifyRefreshToken(refresh_token)
    
    token_data: TokenData | None = Authentication.verify_access_token(refresh_token)

    if not (refresh_token_ok and token_data != None):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or Expired refresh token")

    access_token = Authentication.create_access_token(token_data.role)
    new_refresh_token = Authentication.create_refresh_token(token_data.role)

    db.removeRefreshToken(refresh_token)
    db.addRefreshToken(new_refresh_token, token_data.role)

    response.set_cookie(key="refresh_token", value=new_refresh_token, httponly=True, secure=True, samesite="strict", max_age=REFRESH_TOKEN_EXPIRE_HOURS * 60 * 60)

    return Token(access_token=access_token, token_type="bearer")


@app.post("/clipboard/add")
def add_clipboard(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[Database, Depends(Database.get_db)], content: str):
    
    token_data: TokenData | None = Authentication.verify_access_token(token)

    if (token_data is None):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")
    
    ok = db.addClipboard(token_data.role, content)

    if not ok:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add clipboard")
    
    return {"message": "Clipboard added successfully"}

