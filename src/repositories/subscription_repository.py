from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from datetime import datetime
from src.models.subscription import SubscriptionCreate, SubscriptionUpdate

class SubscriptionRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["subscriptions"]

    def _map_doc(self, doc: dict) -> Optional[dict]:
        if doc:
            doc["id"] = str(doc["_id"])
        return doc

    async def create(self, subscription: SubscriptionCreate) -> dict:
        sub_dict = subscription.model_dump()
        sub_dict["created_at"] = datetime.utcnow()
        sub_dict["updated_at"] = datetime.utcnow()
        sub_dict["is_active"] = True
        if sub_dict.get("starts_at") is None:
            sub_dict["starts_at"] = datetime.utcnow()
        result = await self.collection.insert_one(sub_dict)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        mapped = self._map_doc(doc)
        if mapped is None:
            raise RuntimeError("Failed to retrieve created document")
        return mapped

    async def get_by_tenant(self, tenant_id: str, is_active: Optional[bool] = True) -> Optional[dict]:
        query = {"tenant_id": tenant_id}
        if is_active is not None:
            query = {"tenant_id": tenant_id, "is_active": is_active}

        doc = await self.collection.find_one(query)
        return self._map_doc(doc)

    async def update_by_tenant(self, tenant_id: str, subscription_update: SubscriptionUpdate) -> Optional[dict]:
        update_data = subscription_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_tenant(tenant_id, is_active=True)

        update_data["updated_at"] = datetime.utcnow()

        await self.collection.update_one(
            {"tenant_id": tenant_id},
            {"$set": update_data}
        )

        doc = await self.collection.find_one({"tenant_id": tenant_id})
        return self._map_doc(doc)
