from ollama import AsyncClient
from app.core.config import settings

client = AsyncClient(host=settings.OLLAMA_BASE_URL)

async def generate_response(messages: list[dict]) -> str:
    response = await client.chat(
        model=settings.OLLAMA_MODEL,
        messages=messages
    )

    return response.message.content

async def generate_response_stream(messages: list[dict]):
    stream = await client.chat(
        model=settings.OLLAMA_MODEL,
        messages=messages,
        stream=True
    )

    async for chunk in stream:
        content = chunk.message.content

        if content:
            yield content