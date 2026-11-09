from app.ai.llm import generate_response


async def generate_conversation_title(user_message: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You generate short titles for customer support conversations. "
                "Return only a title of 3 to 6 words. "
                "Do not use quotes or explanations."
            ),
        },
        {
            "role": "user",
            "content": f"Generate a title for this conversation:\n{user_message}",
        },
    ]

    title = await generate_response(messages)

    # Clean and constrain the generated title
    title = title.strip().strip('"\'')
    title = " ".join(title.split())

    return title[:80] if title else "New conversation"