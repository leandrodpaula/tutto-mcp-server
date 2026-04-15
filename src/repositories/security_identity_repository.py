from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase


class SecurityIdentityRepository:
    """Repositório para gerenciar identidades de segurança no MongoDB."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["security_identities"]

    def _map_doc(self, doc: dict) -> Optional[dict]:
        if not doc:
            return None
        mapped = dict(doc)
        mapped["id"] = str(mapped.pop("_id"))
        return mapped

    async def find_by_client_id(self, client_id: str) -> Optional[dict]:
        doc = await self.collection.find_one({"credentials.client_id": client_id})
        return self._map_doc(doc)

    async def create_identity(
        self,
        app_name: str,
        credentials: dict,
        access_control: dict,
        is_active: bool = True,
    ) -> dict:
        now = datetime.now(timezone.utc)
        doc = {
            "app_name": app_name,
            "credentials": credentials,
            "access_control": access_control,
            "is_active": is_active,
            "created_at": now,
            "updated_at": now,
        }
        result = await self.collection.insert_one(doc)
        created = await self.collection.find_one({"_id": result.inserted_id})
        mapped = self._map_doc(created)
        if mapped is None:
            raise RuntimeError("Failed to retrieve created security identity")
        return mapped
