from datetime import datetime
from sqlmodel import Field, SQLModel, DateTime, Column, func


class RefreshToken(SQLModel, table=True):
    __tablename__ = "RefreshTokens"

    refresh_token: str = Field(primary_key=True)
    role: str
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=func.now())
    )


class User(SQLModel, table=True):
    __tablename__ = "Users"

    id: str = Field(primary_key=True)
    ip: str = Field()
    device: str = Field()
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=func.now())
    )
    last_seen: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=func.now())
    )
    platform: str = Field()
