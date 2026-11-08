from app.ai.llm import generate_response
from app.ai.prompts import SYSTEM_PROMPT
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository


class ChatService:

    @staticmethod
    async def send_message(
        conversation_id: str,
        user_id: str,
        content: str
    ):
        # 1. Verify conversation ownership
        conversation = await ConversationRepository.get_by_id(
            conversation_id,
            user_id
        )

        if not conversation:
            return None

        # 2. Save user message
        user_message = await MessageRepository.create(
            conversation_id=conversation_id,
            role="user",
            content=content
        )

        # 3. Retrieve conversation history
        history = await MessageRepository.get_history(conversation_id)

        # 4. Prepare messages for Ollama
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        messages.extend([
            {
                "role": message["role"],
                "content": message["content"]
            }
            for message in history
        ])

        # 5. Generate AI response
        answer = await generate_response(messages)

        # 6. Save assistant response
        assistant_message = await MessageRepository.create(
            conversation_id=conversation_id,
            role="assistant",
            content=answer
        )

        return {
            "user_message": user_message,
            "assistant_message": assistant_message
        }