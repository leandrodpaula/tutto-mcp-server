from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from bson import ObjectId
from datetime import datetime
from src.models.user import UserCreate, UserUpdate

class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["users"]

    def _map_doc(self, doc: dict) -> Optional[dict]:
        if doc:
            doc["id"] = str(doc["_id"])
        return doc

    async def create(self, user: UserCreate) -> dict:
        user_dict = user.model_dump()
        user_dict["is_active"] = True
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()
        result = await self.collection.insert_one(user_dict)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        mapped = self._map_doc(doc)
        if mapped is None:
            raise RuntimeError("Failed to retrieve created document")
        return mapped

    async def get_by_id(self, user_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(user_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(user_id)})
        return self._map_doc(doc)

    async def get_by_phone(self, phone: str, tenant_id: str) -> Optional[dict]:
        doc = await self.collection.find_one({"phone": phone, "tenant_id": tenant_id})
        return self._map_doc(doc)

    async def update(self, user_id: str, user_update: UserUpdate) -> Optional[dict]:
        if not ObjectId.is_valid(user_id):
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(user_id)
            
        update_data["updated_at"] = datetime.utcnow()
        
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        doc = await self.collection.find_one({"_id": ObjectId(user_id)})
        return self._map_doc(doc)

    async def find_by_tenant(self, tenant_id: str) -> List[dict]:
        cursor = self.collection.find({"tenant_id": tenant_id})
        docs = await cursor.to_list(length=100)
        return [self._map_doc(doc) for doc in docs if doc]
