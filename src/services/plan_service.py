from typing import Optional, List
from src.models.plan import PlanCreate, PlanUpdate
from src.repositories.plan_repository import PlanRepository


class PlanServiceError(Exception):
    pass


class PlanService:
    def __init__(self, repository: PlanRepository):
        self.repository = repository

    async def create_plan(self, plan: PlanCreate) -> dict:
        existing = await self.repository.get_by_name(plan.name)
        if existing:
            raise PlanServiceError(f"Plan with name {plan.name} already exists")
        return await self.repository.create(plan)

    async def get_plan_by_name(self, name: str) -> dict:
        plan = await self.repository.get_by_name(name)
        if not plan:
            raise PlanServiceError(f"Plan {name} not found")
        return plan

    async def get_plan_price(self, name: str) -> float:
        plan = await self.get_plan_by_name(name)
        if not plan.get("is_active"):
            raise PlanServiceError(f"Plan {name} is currently inactive")
        return plan.get("price", 0.0)

    async def list_active_plans(self) -> List[dict]:
        return await self.repository.list_active()

    async def update_plan(self, plan_id: str, plan_update: PlanUpdate) -> dict:
        updated = await self.repository.update(plan_id, plan_update)
        if not updated:
            raise PlanServiceError("Plan not found or update failed")
        return updated
