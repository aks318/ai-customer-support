from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.ai.exceptions import (
    LLMConnectionError,
    LLMTimeoutError,
    LLMProviderError,
)
from app.schemas.message import MessageResponse
from app.services.chat_service import ChatService

router = APIRouter()


@router.post(
    "/{conversation_id}/messages/{message_id}/retry",
    response_model=MessageResponse
)
async def retry_message(
    conversation_id: str,
    message_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        result = await ChatService.retry_message(
            conversation_id=conversation_id,
            user_id=current_user["id"],
            message_id=message_id
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )

    except LLMTimeoutError:
        raise HTTPException(
            status_code=504,
            detail="AI response generation timed out"
        )

    except LLMConnectionError:
        raise HTTPException(
            status_code=503,
            detail="AI service is unavailable"
        )

    except LLMProviderError:
        raise HTTPException(
            status_code=502,
            detail="AI service failed"
        )