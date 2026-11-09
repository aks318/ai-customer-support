import json

from app.ai.llm import generate_response
from app.ai.prompts import SYSTEM_PROMPT
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository

from app.ai.llm import generate_response_stream

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

        print("user_message", user_message)

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
            content="",
            status="pending"
        )

        print("assistant_message", assistant_message)

        try:
            answer = await generate_response(messages)

            assistant_message = await MessageRepository.update_generation(
                message_id=assistant_message["id"],
                status="completed",
                content=answer
            )

        except Exception:
            await MessageRepository.update_generation(
                message_id=assistant_message["id"],
                status="failed",
                content=""
            )
            raise

        return {
            "user_message": user_message,
            "assistant_message": assistant_message
        }

    @staticmethod
    async def stream_message(
        conversation_id: str,
        content: str
    ):

         # Save the user's message
        await MessageRepository.create(
            conversation_id=conversation_id,
            role="user",
            content=content
        )

        # Retrieve conversation history
        history = await MessageRepository.get_history(conversation_id)

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        messages.extend([
            {
                "role" : message["role"],
                "content" : message["content"]
            }

            for message in history
        ])

        assistant_message = await MessageRepository.create(
            conversation_id=conversation_id,
            role="assistant",
            content="",
            status="pending"
        )

        # Accumulate the complete response
        full_response = ""

        try:
            async for token in generate_response_stream(messages):
                full_response+=token

                yield(
                    f"data: {json.dumps({"token" : token})}\n\n"
                )
            # Persist the completed assistant response
            assistant_message = await MessageRepository.update_generation(
                message_id=assistant_message["id"],
                status="completed",
                content=full_response
            )

            yield (
                "event: done\n"
                f"data: {json.dumps({'message': assistant_message}, default=str)}\n\n"
            )

        except Exception:
             # Don't expose internal exception details to the client
            await MessageRepository.update_generation(
                message_id=assistant_message["id"],
                status="failed",
                content=full_response
            )
            yield (
                "event: error\n"
                f"data: {json.dumps({'message': 'Unable to generate a response'})}\n\n"
            )