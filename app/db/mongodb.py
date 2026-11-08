from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from app.core.config import settings
from app.db.indexes import create_indexes


class MongoDB:
    client: AsyncMongoClient | None = None
    database: AsyncDatabase | None = None

    @classmethod
    async def connect(cls):
        cls.client = AsyncMongoClient(settings.MONGODB_URL)

        # verify mongodb is reachable
        await cls.client.admin.command("ping")
        
        cls.database = cls.client[settings.MONGODB_DATABASE]
        await create_indexes(cls.database)

        print("Connected to MongoDB")
        print("Database indexex created")

    @classmethod
    async def close(cls):
        if cls.client is not None:
            await cls.client.close()
            cls.client = None
            cls.database = None

            print("Mongodb connection closed")
            