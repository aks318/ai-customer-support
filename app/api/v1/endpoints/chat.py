from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.schemas.message import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

from app.ai.exceptions import (
    LLMConnectionError,
    LLMTimeoutError,
    LLMProviderError,
)

router = APIRouter()


@router.post(
    "/{conversation_id}/chat",
    response_model=ChatResponse
)
async def chat(
    conversation_id: str,
    data: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        result = await ChatService.send_message(
            conversation_id=conversation_id,
            user_id=current_user["id"],
            content=data.content
        )

    except LLMTimeoutError:
        raise HTTPException(
            status_code=504,
            detail="AI response generation timed out"
        )

    except LLMConnectionError:
        raise HTTPException(
            status_code=503,
            detail="AI service is currently unavailable"
        )

    except LLMProviderError:
        raise HTTPException(
            status_code=502,
            detail="AI service failed to generate a response"
        )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    return result