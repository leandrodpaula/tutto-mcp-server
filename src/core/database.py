from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from src.core.config import settings
from typing import Optional

from src.core.logging import get_logger

logger = get_logger(__name__)

class MongoDBManager:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

db_manager = MongoDBManager()

async def connect_to_mongo() -> None:
    if settings.MONGODB_URL:
        db_manager.client = AsyncIOMotorClient(settings.MONGODB_URL)
        db_manager.db = db_manager.client[settings.MONGODB_DATABASE_NAME]
        logger.info(f"Connected to MongoDB at {settings.MONGODB_DATABASE_NAME}")

async def close_mongo_connection() -> None:
    if db_manager.client:
        db_manager.client.close()
        logger.info("MongoDB connection closed")

def get_database() -> AsyncIOMotorDatabase:
    if db_manager.db is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo first.")
    return db_manager.db
