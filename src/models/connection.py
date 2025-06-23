from pydantic import BaseModel, PrivateAttr
from datetime import datetime
from .client import Client
from asyncio import Queue

class Connection(BaseModel):
    id: str
    # client: Client
    queue: Queue

    model_config = {
        "arbitrary_types_allowed": True
    }