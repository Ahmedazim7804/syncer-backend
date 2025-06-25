from pydantic import BaseModel
from datetime import datetime

class Client(BaseModel):
    id: str
    device: str
    created_at: datetime 