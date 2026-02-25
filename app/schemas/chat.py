from pydantic import BaseModel


class ChatSchema(BaseModel):
    session_id: int
    request: str
