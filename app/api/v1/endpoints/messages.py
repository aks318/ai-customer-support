from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.schemas.message import MessageCreate, MessageResponse
from app.services.message_service import MessageService

router = APIRouter()


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_message(
    conversation_id: str,
    data: MessageCreate,
    current_user: dict = Depends(get_current_user)
):
    message = await MessageService.save_user_message(
        conversation_id=conversation_id,
        user_id=current_user["id"],
        content=data.content
    )

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    return message


@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageResponse]
)
async def get_messages(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    messages = await MessageService.get_chat_history(
        conversation_id=conversation_id,
        user_id=current_user["id"]
    )

    if messages is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    return messages