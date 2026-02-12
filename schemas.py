from pydantic import BaseModel


class ChatResponse(BaseModel):
    id: int
    request: str
    response: str


class PromptSchema(BaseModel):
    request: str

