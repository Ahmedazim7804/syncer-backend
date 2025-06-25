from contextlib import AbstractContextManager
from typing import Callable
from sqlmodel import select, Session
from src.schema.auth_schema import RefreshToken, User
from src.models.client import Client
import uuid


class AuthRepository:
    def __init__(self, db_factory: Callable[..., AbstractContextManager[Session]]):
        self.db_factory = db_factory

    def createUser(self, device: str) -> Client:
        user = User(id=str(uuid.uuid4()), device=device)
        with self.db_factory() as db:
            db.add(user)
            db.commit()
            db.refresh(user)
        return Client(id=user.id, device=user.device, created_at=user.created_at)

    def addRefreshToken(self, refresh_token: str, username: str):
        with self.db_factory() as db:
            db.add(RefreshToken(refresh_token=refresh_token, role=username))
            db.commit()

    def removeRefreshToken(self, refresh_token: str):
        with self.db_factory() as db:
            results = db.exec(
                select(RefreshToken).where(RefreshToken.refresh_token == refresh_token)
            ).all()

            for token in results:
                db.delete(token)

            db.commit()

    def refreshTokenExists(self, refresh_token: str) -> bool:
        with self.db_factory() as db:
            results = db.exec(
                select(RefreshToken).where(RefreshToken.refresh_token == refresh_token)
            ).all()
            return len(results) > 0
