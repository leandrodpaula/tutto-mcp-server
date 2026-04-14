from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List, Dict, Any
from bson import ObjectId
from datetime import datetime
from src.models.schedule import ScheduleCreate, ScheduleUpdate


class ScheduleRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["schedules"]

    def _map_doc(self, doc: dict) -> Optional[dict]:
        if doc:
            doc["id"] = str(doc["_id"])
        return doc

    async def create(self, schedule: ScheduleCreate) -> dict:
        schedule_dict = schedule.model_dump()
        schedule_dict["status"] = "pending"
        schedule_dict["created_at"] = datetime.utcnow()
        schedule_dict["updated_at"] = datetime.utcnow()
        result = await self.collection.insert_one(schedule_dict)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        mapped = self._map_doc(doc)
        if mapped is None:
            raise RuntimeError("Failed to retrieve created document")
        return mapped

    async def get_by_id(self, schedule_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(schedule_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(schedule_id)})
        return self._map_doc(doc)

    async def update(self, schedule_id: str, schedule_update: ScheduleUpdate) -> Optional[dict]:
        if not ObjectId.is_valid(schedule_id):
            return None

        update_data = schedule_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(schedule_id)

        update_data["updated_at"] = datetime.utcnow()

        await self.collection.update_one({"_id": ObjectId(schedule_id)}, {"$set": update_data})

        doc = await self.collection.find_one({"_id": ObjectId(schedule_id)})
        return self._map_doc(doc)

    async def find_by_tenant(
        self, tenant_id: str, filters: Optional[Dict[str, Any]] = None
    ) -> List[dict]:
        query: Dict[str, Any] = {"tenant_id": tenant_id}
        if filters:
            if "status" in filters:
                query["status"] = filters["status"]
            if "date_from" in filters and "date_to" in filters:
                query["scheduled_at"] = {
                    "$gte": filters["date_from"],
                    "$lte": filters["date_to"],
                }
            elif "date_from" in filters:
                query["scheduled_at"] = {"$gte": filters["date_from"]}
            elif "date_to" in filters:
                query["scheduled_at"] = {"$lte": filters["date_to"]}

        cursor = self.collection.find(query).sort("scheduled_at", 1)
        docs = await cursor.to_list(length=200)
        return [self._map_doc(doc) for doc in docs if doc]

    async def find_by_user(self, tenant_id: str, user_id: str) -> List[dict]:
        cursor = self.collection.find(
            {
                "tenant_id": tenant_id,
                "user_id": user_id,
            }
        ).sort("scheduled_at", 1)
        docs = await cursor.to_list(length=200)
        return [self._map_doc(doc) for doc in docs if doc]
