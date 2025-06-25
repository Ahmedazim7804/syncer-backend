from datetime import datetime
from sqlmodel import Field, SQLModel, DateTime, Column, func


class ClipboardItem(SQLModel, table=True):
    __tablename__ = "ClipboardItems"

    id: int = Field(primary_key=True, default=None)
    content: str
    role: str
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=func.now())
    )
