from datetime import datetime, timezone

from bson import ObjectId

from app.db.mongodb import MongoDB

from pymongo import ReturnDocument


class MessageRepository:

    @staticmethod
    async def create(
        conversation_id: str,
        role: str,
        content: str,
        status: str = "completed"
    ):
        database = MongoDB.database

        if database is None:
            raise RuntimeError("MongoDB is not connected")

        now = datetime.now(timezone.utc)

        message = {
            "conversation_id": ObjectId(conversation_id),
            "role": role,
            "content": content,
            "status": status,
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
            "status": status,
            "retry_count": 0 if role == "assistant" else 0,
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
                "status": item.get("status", "completed"),
                "created_at": item["created_at"]
            })

        return messages

    @staticmethod
    async def update_generation(
        message_id: str,
        status: str,
        content: str
    ):
        database = MongoDB.database

        if database is None:
            raise RuntimeError("MongoDB is not connected")

        if not ObjectId.is_valid(message_id):
            return None

        result = await database.messages.find_one_and_update(
            {
                "_id": ObjectId(message_id),
                "role": "assistant"
            },
            {
                "$set": {
                    "status": status,
                    "content": content
                }
            },
            return_document=True
        )

        if not result:
            return None

        return {
            "id": str(result["_id"]),
            "conversation_id": str(result["conversation_id"]),
            "role": result["role"],
            "content": result["content"],
            "status": result["status"],
            "created_at": result["created_at"]
        }

    @staticmethod
    async def claim_failed_retry(
        conversation_id: str,
        message_id: str,
        max_retries: int = 3
    ):
        database = MongoDB.database

        if database is None:
            raise RuntimeError("MongoDB is not connected")

        if not ObjectId.is_valid(message_id):
            return None

        message = await database.messages.find_one_and_update(
            {
                "_id": ObjectId(message_id),
                "conversation_id": ObjectId(conversation_id),
                "role": "assistant",
                "status": "failed",
                "$or": [
                    {"retry_count": {"$lt": max_retries}},
                    {"retry_count": {"$exists": False}}
                ]
            },
            {
                "$set": {
                    "status": "pending",
                    "content": ""
                },
                "$inc": {
                    "retry_count": 1
                }
            },
            return_document=ReturnDocument.AFTER
        )

        if not message:
            return None

        return {
            "id": str(message["_id"]),
            "conversation_id": str(message["conversation_id"]),
            "role": message["role"],
            "content": message["content"],
            "status": message["status"],
            "retry_count": message["retry_count"],
            "created_at": message["created_at"]
        }