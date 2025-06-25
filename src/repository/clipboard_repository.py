from contextlib import AbstractContextManager
from typing import Callable
from sqlmodel import select, Session
from src.schema import ClipboardItem


class ClipboardRepository:
    def __init__(self, db_factory: Callable[..., AbstractContextManager[Session]]):
        self.db_factory = db_factory

    def addClipboardItem(self, clipboard: str, username: str) -> bool:
        try:
            with self.db_factory() as db:
                db.add(ClipboardItem(content=clipboard, role=username))
                db.commit()
        except:
            return False

        return True

    def getAllClipboards(self, username: str) -> list[ClipboardItem]:
        with self.db_factory() as db:
            return db.exec(
                select(ClipboardItem).where(ClipboardItem.role == username)
            ).all()
