from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=10000)


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime

class ChatRequest(BaseModel):
    content: str = Field(min_length=1, max_length=10000)
class ChatResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse