from datetime import datetime, timezone
from typing import List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.models.coupon import CouponCreate, CouponUpdate


class CouponRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["coupons"]

    def _map_doc(self, doc: dict) -> Optional[dict]:
        if not doc:
            return None
        mapped = dict(doc)
        mapped["id"] = str(mapped["_id"])
        return mapped

    async def create(self, coupon: CouponCreate) -> dict:
        coupon_dict = coupon.model_dump()
        coupon_dict["created_at"] = datetime.now(timezone.utc)
        coupon_dict["updated_at"] = datetime.now(timezone.utc)
        result = await self.collection.insert_one(coupon_dict)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        mapped = self._map_doc(doc)
        if mapped is None:
            raise RuntimeError("Failed to retrieve created document")
        return mapped

    async def get_by_id(self, coupon_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(coupon_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(coupon_id)})
        return self._map_doc(doc)

    async def get_by_short_code(self, short_code: str) -> Optional[dict]:
        doc = await self.collection.find_one({"short_code": short_code})
        return self._map_doc(doc)

    async def list_active(self) -> List[dict]:
        now = datetime.now(timezone.utc)
        cursor = self.collection.find(
            {
                "is_active": True,
                "start_date": {"$lte": now},
                "$or": [{"end_date": None}, {"end_date": {"$gte": now}}],
            }
        )
        docs = await cursor.to_list(length=100)
        return [self._map_doc(doc) for doc in docs if doc]

    async def update(self, coupon_id: str, coupon_update: CouponUpdate) -> Optional[dict]:
        if not ObjectId.is_valid(coupon_id):
            return None

        update_data = coupon_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(coupon_id)

        update_data["updated_at"] = datetime.now(timezone.utc)

        await self.collection.update_one({"_id": ObjectId(coupon_id)}, {"$set": update_data})

        doc = await self.collection.find_one({"_id": ObjectId(coupon_id)})
        return self._map_doc(doc)

    async def delete(self, coupon_id: str) -> bool:
        if not ObjectId.is_valid(coupon_id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(coupon_id)})
        return result.deleted_count > 0
