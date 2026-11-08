from datetime import datetime, timezone

from bson import ObjectId

from app.db.mongodb import MongoDB


class MessageRepository:

    @staticmethod
    async def create(
        conversation_id: str,
        role: str,
        content: str
    ):
        database = MongoDB.database

        if database is None:
            raise RuntimeError("MongoDB is not connected")

        now = datetime.now(timezone.utc)

        message = {
            "conversation_id": ObjectId(conversation_id),
            "role": role,
            "content": content,
            "created_at": now
        }

        result = await database.messages.insert_one(message)

        await database.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": {"updated_at": now}}
        )

        return {
            "id": str(result.inserted_id),
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "created_at": now
        }

    @staticmethod
    async def get_history(conversation_id: str):
        database = MongoDB.database

        if database is None:
            raise RuntimeError("MongoDB is not connected")

        cursor = database.messages.find(
            {"conversation_id": ObjectId(conversation_id)}
        ).sort("created_at", 1)

        messages = []

        async for item in cursor:
            messages.append({
                "id": str(item["_id"]),
                "conversation_id": str(item["conversation_id"]),
                "role": item["role"],
                "content": item["content"],
                "created_at": item["created_at"]
            })

        return messages