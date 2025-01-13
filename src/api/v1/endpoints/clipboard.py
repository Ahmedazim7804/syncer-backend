from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from src.models.auth import oauth2_scheme, TokenData
from src.models.clipboard import AddClipboardData
from src.core.security import Security
from src.core.container import Container
from dependency_injector.wiring import Provide, inject
from src.services import ClipboardService
from src.core.dependencies import Dependencies

router = APIRouter(
    tags=["clipboard"],
)

USERNAME_DEPENDENCY = Annotated[str, Depends(Dependencies.get_username)]

@router.post("/clipboard/add")
@inject
def add_clipboard(username: USERNAME_DEPENDENCY, data: AddClipboardData, clipboard_service: ClipboardService = Depends(Provide[Container.clipboard_service])):

    ok = clipboard_service.addClipboard(clipboard=data.content, username=username)

    if not ok:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add clipboard")
    
    return {"message": "Clipboard added successfully"}


@router.get("/clipboard/all")
@inject
def get_clipboard(username: USERNAME_DEPENDENCY, clipboard_service: ClipboardService = Depends(Provide[Container.clipboard_service])) -> list[str]:

    clips = clipboard_service.getClipboards(username=username)

    print(clips)

    return clips
