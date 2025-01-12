from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from src.models.auth import oauth2_scheme, TokenData
from src.models.clipboard import AddClipboardData
from src.core.security import Security 
from src.core.container import Container
from dependency_injector.wiring import Provide, inject
from src.services import ClipboardService

router = APIRouter(
    tags=["clipboard"],
)

@router.post("/clipboard/add")
@inject
def add_clipboard(token: Annotated[str, Depends(oauth2_scheme)], data: AddClipboardData, clipboard_service: ClipboardService = Depends(Provide[Container.clipboard_service])):

    token_data: TokenData = Security.getTokenData(token)

    ok = clipboard_service.addClipboard(clipboard=data.content, username=token_data.role)

    if not ok:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add clipboard")
    
    return {"message": "Clipboard added successfully"}