from fastmcp import FastMCP
from typing import Optional, List, Dict, Any
from bson import ObjectId
from datetime import datetime
from src.core.database import get_database

def register_worker_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    async def fetch_pending_events(collection_name: str) -> List[Dict[str, Any]]:
        """
        Fetch pending message events from the specified collection.
        """
        db = get_database()
        cursor = db[collection_name].find({"status": "pending", "type": "message"})
        events = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            events.append(doc)
        return events

    @mcp.tool()
    async def update_event_status(collection_name: str, event_id: str, status: str, error: Optional[str] = None) -> bool:
        """
        Update the status of an event.
        """
        db = get_database()
        update_data = {"status": status, "updated_at": datetime.now()}
        if error:
            update_data["error"] = error
            
        result = await db[collection_name].update_one(
            {"_id": ObjectId(event_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0

    @mcp.tool()
    async def get_customer_for_worker(customer_id: str, phone: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an active customer by customerId and phone.
        """
        db = get_database()
        customer = await db["customers"].find_one({
            "customerId": customer_id,
            "phone": phone,
            "is_active": True
        })
        if customer:
            customer["_id"] = str(customer["_id"])
        return customer

    @mcp.tool()
    async def get_agent_for_worker(name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve agent configuration by name.
        """
        db = get_database()
        agent = await db["agents"].find_one({"name": name})
        if agent:
            agent["_id"] = str(agent["_id"])
        return agent

    @mcp.tool()
    async def insert_event_response(collection_name: str, response_data: Dict[str, Any]) -> str:
        """
        Insert a new event (usually a response) into the specified collection.
        """
        db = get_database()
        if "created_at" not in response_data:
            response_data["created_at"] = datetime.now()
        if "updated_at" not in response_data:
            response_data["updated_at"] = datetime.now()
            
        result = await db[collection_name].insert_one(response_data)
        return str(result.inserted_id)
