from datetime import datetime, timedelta, timezone
from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.core.config import settings
from src.models.session import SessionCreate


class SessionRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["sessions"]

    def _map_doc(self, doc: dict) -> Optional[dict]:
        if not doc:
            return None
        mapped = dict(doc)
        mapped["id"] = str(mapped["_id"])
        return mapped

    async def create(self, session: SessionCreate) -> dict:
        session_dict = session.model_dump()
        session_dict["created_at"] = datetime.now(timezone.utc)
        session_dict["expires_at"] = datetime.now(timezone.utc) + timedelta(days=settings.SESSION_TTL_DAYS)
        session_dict["is_active"] = True
        result = await self.collection.insert_one(session_dict)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        mapped = self._map_doc(doc)
        if mapped is None:
            raise RuntimeError("Failed to retrieve created document")
        return mapped

    async def get_by_user(self, user_id: str, tenant_id: str) -> List[dict]:
        cursor = self.collection.find({"user_id": user_id, "tenant_id": tenant_id}).sort(
            "created_at", 1
        )
        docs = await cursor.to_list(length=1000)
        return [self._map_doc(doc) for doc in docs if doc]
