from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.deps import get_current_user
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.message import ChatRequest
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("/{conversation_id}/chat/stream")
async def stream_chat(
    conversation_id: str,
    data: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    # Validate ownership before starting the stream
    conversation = await ConversationRepository.get_by_id(
        conversation_id,
        current_user["id"]
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    return StreamingResponse(
        ChatService.stream_message(
            conversation_id=conversation_id,
            content=data.content
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )