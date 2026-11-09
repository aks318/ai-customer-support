import json

from app.ai.llm import generate_response
from app.ai.prompts import SYSTEM_PROMPT
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository

from app.ai.llm import generate_response_stream
from app.ai.exceptions import (
    LLMConnectionError,
    LLMTimeoutError,
    LLMProviderError,
)

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

        except LLMTimeoutError:
            await MessageRepository.update_generation(
                message_id=assistant_message["id"],
                status="failed",
                content=full_response
            )

            yield (
                "event: error\n"
                'data: {"code": "timeout", '
                '"message": "AI response timed out"}\n\n'
            )

        except LLMConnectionError:
            await MessageRepository.update_generation(
                message_id=assistant_message["id"],
                status="failed",
                content=full_response
            )

            yield (
                "event: error\n"
                'data: {"code": "unavailable", '
                '"message": "AI service unavailable"}\n\n'
            )

        except Exception:
            await MessageRepository.update_generation(
                message_id=assistant_message["id"],
                status="failed",
                content=full_response
            )

            yield (
                "event: error\n"
                'data: {"code": "generation_failed", '
                '"message": "Unable to generate response"}\n\n'
            )

    @staticmethod
    async def retry_message(
        conversation_id: str,
        user_id: str,
        message_id: str
    ):
        # 1. Validate conversation ownership
        conversation = await ConversationRepository.get_by_id(
            conversation_id,
            user_id
        )

        if not conversation:
            return None

        # 2. Atomically claim the failed message
        assistant_message = await MessageRepository.claim_failed_retry(
            conversation_id=conversation_id,
            message_id=message_id,
            max_retries=3
        )

        if not assistant_message:
            raise ValueError(
                "Message cannot be retried or retry limit exceeded"
            )

        # 3. Retrieve conversation history
        history = await MessageRepository.get_history(conversation_id)

        # 4. Exclude the failed assistant message and anything after it
        message_index = next(
            (
                index
                for index, message in enumerate(history)
                if message["id"] == message_id
            ),
            None
        )

        if message_index is None:
            raise RuntimeError("Message not found in conversation history")

        previous_history = history[:message_index]

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
            for message in previous_history
        ])

        # 5. Generate and update the existing assistant message
        try:
            answer = await generate_response(messages)

            return await MessageRepository.update_generation(
                message_id=message_id,
                status="completed",
                content=answer
            )

        except Exception:
            await MessageRepository.update_generation(
                message_id=message_id,
                status="failed",
                content=""
            )
            raise