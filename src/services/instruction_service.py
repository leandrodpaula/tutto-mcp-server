from typing import List, Optional

from src.models.instruction import InstructionCreate
from src.repositories.instruction_repository import InstructionRepository


class InstructionService:
    def __init__(self, repository: InstructionRepository):
        self.repository = repository

    async def add_instruction(self, instruction: InstructionCreate) -> dict:
        return await self.repository.create(instruction)

    async def list_tenant_instructions(self, tenant_id: str) -> List[dict]:
        return await self.repository.find_by_tenant(tenant_id)

    async def search_instructions(self, tenant_id: str, query: str) -> List[dict]:
        return await self.repository.search(tenant_id, query)

    async def remove_instruction(self, instruction_id: str) -> Optional[dict]:
        instruction = await self.repository.get_by_id(instruction_id)
        if not instruction:
            raise ValueError("Instruction not found")
        return await self.repository.update(instruction_id, {"is_active": False})

    async def update_instruction(
        self, instruction_id: str, instruction: InstructionCreate
    ) -> Optional[dict]:
        existing = await self.repository.get_by_id(instruction_id)
        if not existing:
            raise ValueError("Instruction not found")
        return await self.repository.update(instruction_id, instruction)
