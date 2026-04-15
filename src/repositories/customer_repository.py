from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


class CustomerRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["customers"]

    def _map_doc(self, doc: dict) -> Optional[dict]:
        if not doc:
            return None
        mapped = dict(doc)
        mapped["id"] = str(mapped["_id"])
        return mapped

    async def create(self, data: dict) -> dict:
        now = datetime.now(timezone.utc)
        data["created_at"] = now
        data["updated_at"] = now
        result = await self.collection.insert_one(data)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        mapped = self._map_doc(doc)
        if mapped is None:
            raise RuntimeError("Failed to retrieve created customer document")
        return mapped

    async def get_by_id(self, customer_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(customer_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(customer_id)})
        return self._map_doc(doc)

    async def get_by_email(self, email: str) -> Optional[dict]:
        doc = await self.collection.find_one({"email": email.lower().strip()})
        return self._map_doc(doc)

    async def get_by_phone(self, phone: str) -> Optional[dict]:
        doc = await self.collection.find_one({"phone": phone})
        return self._map_doc(doc)

    async def get_by_google_id(self, google_id: str) -> Optional[dict]:
        doc = await self.collection.find_one({"google_id": google_id})
        return self._map_doc(doc)

    async def update(self, customer_id: str, data: dict) -> Optional[dict]:
        if not ObjectId.is_valid(customer_id):
            return None
        data["updated_at"] = datetime.now(timezone.utc)
        await self.collection.update_one({"_id": ObjectId(customer_id)}, {"$set": data})
        return await self.get_by_id(customer_id)
