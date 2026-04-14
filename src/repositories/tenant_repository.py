from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.models.tenant import TenantCreate


class TenantRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["tenants"]

    def _map_doc(self, doc: dict) -> Optional[dict]:
        if doc:
            doc["id"] = str(doc["_id"])
        return doc

    async def create(self, tenant: TenantCreate) -> dict:
        tenant_dict = tenant.model_dump()
        result = await self.collection.insert_one(tenant_dict)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        mapped = self._map_doc(doc)
        if mapped is None:
            raise RuntimeError("Failed to retrieve created document")
        return mapped

    async def get_by_id(self, tenant_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(tenant_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(tenant_id)})
        return self._map_doc(doc)

    async def get_by_phone(self, phone: str) -> Optional[dict]:
        doc = await self.collection.find_one({"phone": phone})
        return self._map_doc(doc)

    async def get_by_token(self, token: str) -> Optional[dict]:
        doc = await self.collection.find_one({"token": token})
        return self._map_doc(doc)

    async def update(self, tenant_id: str, data: dict) -> Optional[dict]:
        if not ObjectId.is_valid(tenant_id):
            return None
        from datetime import datetime, timezone

        data["updated_at"] = datetime.now(timezone.utc)
        await self.collection.update_one({"_id": ObjectId(tenant_id)}, {"$set": data})
        return await self.get_by_id(tenant_id)
