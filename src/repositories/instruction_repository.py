from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List, Union
from bson import ObjectId
from datetime import datetime
from src.models.instruction import InstructionCreate

class InstructionRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        # Using the same collection name as user did for services to potentially migrate or just follow his lead
        self.collection = db["tenants_instructions"]

    def _map_doc(self, doc: dict) -> dict:
        doc["id"] = str(doc["_id"])
        return doc

    async def create(self, instruction: InstructionCreate) -> dict:
        instruction_dict = instruction.model_dump()
        instruction_dict["created_at"] = datetime.utcnow()
        instruction_dict["updated_at"] = datetime.utcnow()
        instruction_dict["is_active"] = True
        result = await self.collection.insert_one(instruction_dict)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        mapped = self._map_doc(doc)
        if mapped is None:
            raise RuntimeError("Failed to retrieve created document")
        return mapped

    async def get_by_id(self, instruction_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(instruction_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(instruction_id)})
        return self._map_doc(doc) if doc else None

    async def update(self, instruction_id: str, instruction: Union[InstructionCreate, dict]) -> Optional[dict]:
        if not ObjectId.is_valid(instruction_id):
            return None
        
        if isinstance(instruction, InstructionCreate):
            update_data = instruction.model_dump(exclude_unset=True)
        else:
            update_data = instruction
            
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(instruction_id)},
            {"$set": update_data}
        )
        
        doc = await self.collection.find_one({"_id": ObjectId(instruction_id)})
        return self._map_doc(doc) if doc else None

    async def find_by_tenant(self, tenant_id: str) -> List[dict]:
        cursor = self.collection.find({"tenant_id": tenant_id, "is_active": True})
        docs = await cursor.to_list(length=100)
        return [self._map_doc(doc) for doc in docs if doc]

    async def search(self, tenant_id: str, query: str) -> List[dict]:
        cursor = self.collection.find({
            "tenant_id": tenant_id,
            "is_active": True,
            "name": {"$regex": query, "$options": "i"}
        })
        docs = await cursor.to_list(length=100)
        return [self._map_doc(doc) for doc in docs if doc]
