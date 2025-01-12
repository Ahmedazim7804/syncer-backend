from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, Callable
from src.core.database import Database
from src.models.auth import oauth2_scheme, TokenData
from src.models.clipboard import AddClipboardData
from src.core.security import Security 
from contextlib import AbstractContextManager
from sqlmodel import Session

router = APIRouter(
    tags=["clipboard"],
)

@router.post("/clipboard/add")
def add_clipboard(token: Annotated[str, Depends(oauth2_scheme)], data: AddClipboardData):

    # with db_factory() as db:
    token_data: TokenData | None = Security.verify_access_token(token)

    if (token_data is None):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    # ok = db.addClipboard(token_data.role, data.content)

    # if not ok:
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add clipboard")
    
    return {"message": "Clipboard added successfully"}