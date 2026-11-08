from app.repositories.message_repository import MessageRepository
from app.repositories.conversation_repository import ConversationRepository


class MessageService:

    @staticmethod
    async def save_user_message(
        conversation_id: str,
        user_id: str,
        content: str
    ):
        # Verify conversation ownership
        conversation = await ConversationRepository.get_by_id(
            conversation_id,
            user_id
        )

        if not conversation:
            return None

        return await MessageRepository.create(
            conversation_id=conversation_id,
            role="user",
            content=content
        )

    @staticmethod
    async def get_chat_history(
        conversation_id: str,
        user_id: str
    ):
        # Verify conversation ownership
        conversation = await ConversationRepository.get_by_id(
            conversation_id,
            user_id
        )

        if not conversation:
            return None

        return await MessageRepository.get_history(conversation_id)