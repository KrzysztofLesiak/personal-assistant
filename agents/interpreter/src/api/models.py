from pydantic import BaseModel
from typing import List, Dict, Any


class MessageResponse(BaseModel):
    content: str
    tokens_used: int


class ChatRequest(BaseModel):
    messages: List[Dict[str, Any]]
    stream: bool = False


class ChatResponse(BaseModel):
    message: MessageResponse