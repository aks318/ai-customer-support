from pymongo import ASCENDING, DESCENDING


async def create_indexes(database):

    # Users
    await database.users.create_index(
        [("email", ASCENDING)],
        unique=True,
        name="unique_user_email"
    )

    # Conversations
    await database.conversations.create_index(
        [
            ("user_id", ASCENDING),
            ("updated_at", DESCENDING)
        ],
        name="user_conversations"
    )

    # Messages
    await database.messages.create_index(
        [
            ("conversation_id", ASCENDING),
            ("created_at", ASCENDING)
        ],
        name="conversation_messages"
    )