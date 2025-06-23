from pydantic import BaseModel
from datetime import datetime

class Client(BaseModel):
    id: str
    name: str
    joined_at: datetime 