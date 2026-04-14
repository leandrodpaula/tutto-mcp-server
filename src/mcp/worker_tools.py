from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from fastmcp import FastMCP

from src.core.database import get_database
from src.core.logging import get_logger

logger = get_logger(__name__)


def register_worker_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    async def fetch_pending_events(collection_name: str) -> List[Dict[str, Any]]:
        """
        Fetch pending message events from the specified collection.
        """
        try:
            db = get_database()
            cursor = db[collection_name].find({"status": "pending", "type": "message"})
            events = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                events.append(doc)
            return events
        except Exception as e:
            logger.error(f"Error fetching pending events from {collection_name}: {str(e)}")
            raise

    @mcp.tool()
    async def update_event_status(
        collection_name: str, event_id: str, status: str, error: Optional[str] = None
    ) -> bool:
        """
        Update the status of an event.
        """
        try:
            db = get_database()
            update_data = {"status": status, "updated_at": datetime.now()}
            if error:
                update_data["error"] = error

            result = await db[collection_name].update_one(
                {"_id": ObjectId(event_id)}, {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(
                f"Error updating event status for {event_id} in {collection_name}: {str(e)}"
            )
            raise

    @mcp.tool()
    async def get_customer_for_worker(customer_id: str, phone: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an active customer by customerId and phone.
        """
        try:
            db = get_database()
            customer = await db["customers"].find_one(
                {"customerId": customer_id, "phone": phone, "is_active": True}
            )
            if customer:
                customer["_id"] = str(customer["_id"])
            return customer
        except Exception as e:
            logger.error(f"Error getting customer {customer_id} ({phone}): {str(e)}")
            raise

    @mcp.tool()
    async def get_agent_for_worker(name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve agent configuration by name.
        """
        try:
            db = get_database()
            agent = await db["agents"].find_one({"name": name})
            if agent:
                agent["_id"] = str(agent["_id"])
            return agent
        except Exception as e:
            logger.error(f"Error getting agent {name}: {str(e)}")
            raise

    @mcp.tool()
    async def insert_event_response(collection_name: str, response_data: Dict[str, Any]) -> str:
        """
        Insert a new event (usually a response) into the specified collection.
        """
        try:
            db = get_database()
            if "created_at" not in response_data:
                response_data["created_at"] = datetime.now()
            if "updated_at" not in response_data:
                response_data["updated_at"] = datetime.now()

            result = await db[collection_name].insert_one(response_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting event response into {collection_name}: {str(e)}")
            raise
