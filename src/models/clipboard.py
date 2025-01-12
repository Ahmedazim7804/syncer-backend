from pydantic import BaseModel

class AddClipboardData(BaseModel):
    content: str