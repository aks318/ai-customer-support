from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse
)
from app.services.conversation_service import ConversationService

router = APIRouter()


@router.post(
    "/",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_conversation(
    data: ConversationCreate,
    current_user: dict = Depends(get_current_user)
):
    return await ConversationService.create_conversation(
        current_user["id"],
        data.title
    )


@router.get(
    "/",
    response_model=list[ConversationResponse]
)
async def get_conversations(
    current_user: dict = Depends(get_current_user)
):
    return await ConversationService.get_conversations(
        current_user["id"]
    )


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse
)
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    conversation = await ConversationService.get_conversation(
        conversation_id,
        current_user["id"]
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    return conversation


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    deleted = await ConversationService.delete_conversation(
        conversation_id,
        current_user["id"]
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )