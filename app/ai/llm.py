import asyncio
import httpx

from ollama import AsyncClient

from app.ai.exceptions import (
    LLMConnectionError,
    LLMTimeoutError,
    LLMProviderError,
)
from app.core.config import settings


client = AsyncClient(host=settings.OLLAMA_BASE_URL)


async def generate_response(messages: list[dict]) -> str:
    try:
        async with asyncio.timeout(settings.LLM_TIMEOUT_SECONDS):
            response = await client.chat(
                model=settings.OLLAMA_MODEL,
                messages=messages
            )

        return response.message.content

    except TimeoutError as error:
        raise LLMTimeoutError("LLM generation timed out") from error

    except httpx.ConnectError as error:
        raise LLMConnectionError("Cannot connect to Ollama") from error

    except httpx.HTTPError as error:
        raise LLMProviderError("Ollama request failed") from error

    except Exception as error:
        raise LLMProviderError("LLM generation failed") from error


async def generate_response_stream(messages: list[dict]):
    try:
        async with asyncio.timeout(settings.LLM_TIMEOUT_SECONDS):
            stream = await client.chat(
                model=settings.OLLAMA_MODEL,
                messages=messages,
                stream=True
            )

            async for chunk in stream:
                content = chunk.message.content

                if content:
                    yield content

    except TimeoutError as error:
        raise LLMTimeoutError("LLM generation timed out") from error

    except httpx.ConnectError as error:
        raise LLMConnectionError("Cannot connect to Ollama") from error

    except httpx.HTTPError as error:
        raise LLMProviderError("Ollama request failed") from error

    except Exception as error:
        raise LLMProviderError("LLM generation failed") from error