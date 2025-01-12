from datetime import datetime
from sqlmodel import Field, SQLModel, DateTime, Column, func

class RefreshToken(SQLModel, table=True):

    __tablename__ = "RefreshTokens"

    refresh_token: str = Field(primary_key=True)
    role: str
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=func.now()))