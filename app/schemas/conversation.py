from datetime import datetime

from pydantic import BaseModel, Field

class ConversationCreate(BaseModel):
    title: str = Field(
        default="New Conversation",
        min_length=1,
        max_length=150
    )

class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime