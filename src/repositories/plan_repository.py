from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from bson import ObjectId
from datetime import datetime
from src.models.plan import PlanCreate, PlanUpdate


class PlanRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["plans"]

    def _map_doc(self, doc: dict) -> Optional[dict]:
        if doc:
            doc["id"] = str(doc["_id"])
        return doc

    async def create(self, plan: PlanCreate) -> dict:
        plan_dict = plan.model_dump()
        plan_dict["created_at"] = datetime.utcnow()
        plan_dict["updated_at"] = datetime.utcnow()
        plan_dict["price_history"] = [
            {"price": plan.price, "changed_at": datetime.utcnow(), "reason": "Initial price"}
        ]
        result = await self.collection.insert_one(plan_dict)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        mapped = self._map_doc(doc)
        if mapped is None:
            raise RuntimeError("Failed to retrieve created document")
        return mapped

    async def get_by_id(self, plan_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(plan_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(plan_id)})
        return self._map_doc(doc)

    async def get_by_name(self, name: str) -> Optional[dict]:
        doc = await self.collection.find_one({"name": name})
        return self._map_doc(doc)

    async def list_active(self) -> List[dict]:
        cursor = self.collection.find({"is_active": True})
        docs = await cursor.to_list(length=100)
        return [self._map_doc(doc) for doc in docs if doc is not None]  # type: ignore

    async def update(self, plan_id: str, plan_update: PlanUpdate) -> Optional[dict]:
        if not ObjectId.is_valid(plan_id):
            return None

        # Fetch current to compare price
        current = await self.collection.find_one({"_id": ObjectId(plan_id)})
        if not current:
            return None

        update_data = plan_update.model_dump(exclude_unset=True)
        change_reason = update_data.pop("change_reason", None)

        if not update_data:
            return self._map_doc(current)

        # If price changed, add to history
        if "price" in update_data and update_data["price"] != current.get("price"):
            history_entry = {
                "price": update_data["price"],
                "changed_at": datetime.utcnow(),
                "reason": change_reason or "Price update",
            }
            await self.collection.update_one(
                {"_id": ObjectId(plan_id)}, {"$push": {"price_history": history_entry}}
            )

        update_data["updated_at"] = datetime.utcnow()

        await self.collection.update_one({"_id": ObjectId(plan_id)}, {"$set": update_data})

        doc = await self.collection.find_one({"_id": ObjectId(plan_id)})
        return self._map_doc(doc)

    async def delete(self, plan_id: str) -> bool:
        if not ObjectId.is_valid(plan_id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(plan_id)})
        return result.deleted_count > 0
