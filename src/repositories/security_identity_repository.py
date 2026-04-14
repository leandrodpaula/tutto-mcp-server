from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase


class SecurityIdentityRepository:
    """Repositório para gerenciar identidades de segurança no MongoDB."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["security_identities"]

    def _map_doc(self, doc: Optional[dict]) -> Optional[dict]:
        if doc:
            doc["id"] = str(doc.pop("_id"))
        return doc

    async def find_by_client_id(self, client_id: str) -> Optional[dict]:
        doc = await self.collection.find_one({"client_id": client_id})
        return self._map_doc(doc)

    async def create_identity(
        self,
        client_id: str,
        client_secret: str,
        name: Optional[str] = None,
        scopes: Optional[list] = None,
        enabled: bool = True,
    ) -> dict:
        doc = {
            "client_id": client_id,
            "client_secret": client_secret,
            "name": name,
            "scopes": scopes or [],
            "enabled": enabled,
            "created_at": datetime.now(timezone.utc),
        }
        result = await self.collection.insert_one(doc)
        created = await self.collection.find_one({"_id": result.inserted_id})
        mapped = self._map_doc(created)
        if mapped is None:
            raise RuntimeError("Failed to retrieve created security identity")
        return mapped
