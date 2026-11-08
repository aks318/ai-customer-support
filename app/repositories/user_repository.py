from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError
from app.db.mongodb import MongoDB


class UserRepository:
    @staticmethod
    async def create_user(user_data: dict) -> dict:
        database = MongoDB.database

        if database is None:
            raise RuntimeError("MongoDB is not Connected")

        user_data["created_at"] = datetime.now(timezone.utc)
        try:
            result = await database.users.insert_one(user_data)
            return {
                "id" : str(result.inserted_id),
                "name" : user_data["name"],
                "email" : user_data["email"],
            }
        except DuplicateKeyError:
            raise ValueError("Email already registered")
