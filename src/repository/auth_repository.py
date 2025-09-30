from contextlib import AbstractContextManager
from typing import Callable
from sqlmodel import select, Session
from src.schema.auth_schema import RefreshToken, User
from src.models.client import Client
import uuid
from typing import Optional
from datetime import datetime


class AuthRepository:
    def __init__(self, db_factory: Callable[..., AbstractContextManager[Session]]):
        self.db_factory = db_factory

    def createUser(
        self,
        id: str,
        ip: str,
        device: str,
        platform: str,
    ) -> Client:
        # CHECK EXISTING USER
        with self.db_factory() as db:
            existing_users = db.exec(select(User).where(User.id == id)).all()
            user = None;
            if (len(existing_users) == 0):
                user = User(id=id, device=device, platform=platform, ip=ip)
            else:
                user = existing_users[0]
                user.ip = ip
                user.device = device

            db.add(user)
            db.commit()
            db.refresh(user)

            return Client(
                id=user.id,
                ip=user.ip,
                platform=user.platform,
                device=user.device,
                created_at=user.created_at,
                last_seen=user.last_seen,
            )


    def getUser(self, id: str) -> Client:
        with self.db_factory() as db:
            user = db.exec(select(User).where(User.id == id)).first()
            return Client(
                id=user.id,
                ip=user.ip,
                platform=user.platform,
                device=user.device,
                created_at=user.created_at,
                last_seen=user.last_seen,
            )

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

    def updateUser(self, id: str, device: Optional[str] = None, ip: Optional[str] = None, last_seen: Optional[datetime] = None):
        with self.db_factory() as db:
            results = db.exec(select(User).where(User.id == id)).all()
            if (len(results) == 0):
                return
            else:
                result = results[0]
                if (device is not None):
                    result.device = device
                if (ip is not None):
                    result.ip = ip
                if (last_seen is not None):
                    result.last_seen = last_seen

                db.add(result)
                db.commit()
                db.refresh(result)

    def getAllUsers(self):
        with self.db_factory() as db:
            return db.exec(select(User)).all()