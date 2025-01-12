from datetime import datetime
from sqlmodel import Field, SQLModel, DateTime, Column, func

class Clipboard(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    content: str
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=func.now()))