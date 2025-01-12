
from fastapi import APIRouter

from src.api.v1.endpoints.auth import router as auth_router
from src.api.v1.endpoints.clipboard import router as clipboard_router

routers = APIRouter(
    prefix="/api/v1",
    tags=["v1"],
)

routers.tags.append("v1")
routers.include_router(auth_router)
routers.include_router(clipboard_router)
