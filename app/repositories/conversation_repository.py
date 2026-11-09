from datetime import datetime, timezone

from bson import ObjectId

from app.db.mongodb import MongoDB


class ConversationRepository:

    @staticmethod
    async def create(user_id: str, title: str):
        database = MongoDB.database

        if database is None:
            raise RuntimeError("MongoDB is not connected")

        now = datetime.now(timezone.utc)

        conversation = {
            "user_id": ObjectId(user_id),
            "title": title,
            "created_at": now,
            "updated_at": now
        }

        result = await database.conversations.insert_one(conversation)

        return {
            "id": str(result.inserted_id),
            "title": title,
            "created_at": now,
            "updated_at": now
        }

    @staticmethod
    async def get_all(user_id: str):
        database = MongoDB.database

        if database is None:
            raise RuntimeError("MongoDB is not connected")

        cursor = database.conversations.find(
            {"user_id": ObjectId(user_id)}
        ).sort("updated_at", -1)

        conversations = []

        async for item in cursor:
            conversations.append({
                "id": str(item["_id"]),
                "title": item["title"],
                "created_at": item["created_at"],
                "updated_at": item["updated_at"]
            })

        return conversations

    @staticmethod
    async def get_by_id(conversation_id: str, user_id: str):
        database = MongoDB.database

        if database is None:
            raise RuntimeError("MongoDB is not connected")

        if not ObjectId.is_valid(conversation_id):
            return None

        conversation = await database.conversations.find_one({
            "_id": ObjectId(conversation_id),
            "user_id": ObjectId(user_id)
        })

        if not conversation:
            return None

        return {
            "id": str(conversation["_id"]),
            "title": conversation["title"],
            "created_at": conversation["created_at"],
            "updated_at": conversation["updated_at"]
        }

    @staticmethod
    async def delete(conversation_id: str, user_id: str):
        database = MongoDB.database

        if database is None:
            raise RuntimeError("MongoDB is not connected")

        if not ObjectId.is_valid(conversation_id):
            return False

        result = await database.conversations.delete_one({
            "_id": ObjectId(conversation_id),
            "user_id": ObjectId(user_id)
        })

        return result.deleted_count > 0

    @staticmethod
    async def update_title(
        conversation_id: str,
        user_id: str,
        title: str,
    ):
        from bson import ObjectId

        result = await MongoDB.database.conversations.update_one(
            {
                "_id": ObjectId(conversation_id),
                "user_id": ObjectId(user_id),
            },
            {
                "$set": {
                    "title": title,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

        return result.modified_count > 0