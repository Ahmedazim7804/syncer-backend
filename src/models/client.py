from pydantic import BaseModel
from datetime import datetime


class Client(BaseModel):
    id: str
    ip: str
    device: str
    platform: str
    created_at: datetime
    last_seen: datetime
