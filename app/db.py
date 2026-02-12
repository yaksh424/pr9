from motor.motor_asyncio import AsyncIOMotorClient
from os import getenv

MONGO_URI = getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = getenv("MONGO_DB", "olivander_shop")

client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global client
    if client is None:
        client = AsyncIOMotorClient(MONGO_URI)
    return client


def get_db():
    return get_client()[MONGO_DB]
