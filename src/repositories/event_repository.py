from datetime import datetime, timezone
from typing import Any, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase


class EventRepository:
    """Repositório genérico para persistir eventos recebidos via webhook."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["events"]

    def _map_doc(self, doc: Optional[dict]) -> Optional[dict]:
        if doc:
            doc["id"] = str(doc.pop("_id"))
        return doc

    async def create_webhook_event(
        self,
        event: str,
        instance: str,
        data: Any,
        destination: Optional[str] = None,
        date_time: Optional[str] = None,
        sender: Optional[str] = None,
        server_url: Optional[str] = None,
        apikey: Optional[str] = None,
    ) -> dict:
        doc = {
            "event": event,
            "instance": instance,
            "data": data,
            "destination": destination,
            "date_time": date_time,
            "sender": sender,
            "server_url": server_url,
            "apikey": apikey,
            "received_at": datetime.now(timezone.utc),
        }
        result = await self.collection.insert_one(doc)
        created = await self.collection.find_one({"_id": result.inserted_id})
        mapped = self._map_doc(created)
        if mapped is None:
            raise RuntimeError("Failed to retrieve created webhook event")
        return mapped
