from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from bson import ObjectId
from src.models.message import MessageCreate
from datetime import datetime, timezone

class MessageRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["messages"]

    def _map_doc(self, doc: dict) -> Optional[dict]:
        if doc:
            doc["id"] = str(doc["_id"])
        return doc

    async def create(self, message: MessageCreate, status: str = "pending") -> dict:
        message_dict = message.model_dump()
        
        now = datetime.now(timezone.utc)
        message_dict["status"] = status
        message_dict["created_at"] = now
        message_dict["updated_at"] = now

        result = await self.collection.insert_one(message_dict)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        mapped = self._map_doc(doc)
        if mapped is None:
            raise RuntimeError("Failed to retrieve created document")
        return mapped
