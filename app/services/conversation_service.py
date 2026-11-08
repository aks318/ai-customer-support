from app.repositories.conversation_repository import ConversationRepository


class ConversationService:

    @staticmethod
    async def create_conversation(user_id: str, title: str):
        return await ConversationRepository.create(user_id, title)

    @staticmethod
    async def get_conversations(user_id: str):
        return await ConversationRepository.get_all(user_id)

    @staticmethod
    async def get_conversation(
        conversation_id: str,
        user_id: str
    ):
        return await ConversationRepository.get_by_id(
            conversation_id,
            user_id
        )

    @staticmethod
    async def delete_conversation(
        conversation_id: str,
        user_id: str
    ):
        return await ConversationRepository.delete(
            conversation_id,
            user_id
        )