from typing import Optional, List, Dict, Any
from src.models.schedule import ScheduleCreate, ScheduleUpdate
from src.repositories.schedule_repository import ScheduleRepository


class ScheduleServiceError(Exception):
    pass


class ScheduleService:
    def __init__(self, repository: ScheduleRepository):
        self.repository = repository

    async def create_schedule(self, schedule: ScheduleCreate) -> dict:
        created = await self.repository.create(schedule)
        return created

    async def get_schedule(self, schedule_id: str) -> dict:
        schedule = await self.repository.get_by_id(schedule_id)
        if not schedule:
            raise ScheduleServiceError("Schedule not found")
        return schedule

    async def list_schedules(
        self, tenant_id: str, filters: Optional[Dict[str, Any]] = None
    ) -> List[dict]:
        return await self.repository.find_by_tenant(tenant_id, filters)

    async def list_user_schedules(self, tenant_id: str, user_id: str) -> List[dict]:
        return await self.repository.find_by_user(tenant_id, user_id)

    async def update_schedule(self, schedule_id: str, schedule_update: ScheduleUpdate) -> dict:
        updated = await self.repository.update(schedule_id, schedule_update)
        if not updated:
            raise ScheduleServiceError("Schedule not found or update failed")
        return updated

    async def cancel_schedule(self, schedule_id: str) -> dict:
        schedule = await self.repository.get_by_id(schedule_id)
        if not schedule:
            raise ScheduleServiceError("Schedule not found")
        cancel_update = ScheduleUpdate(status="cancelled")
        updated = await self.repository.update(schedule_id, cancel_update)
        if not updated:
            raise ScheduleServiceError("Failed to cancel schedule")
        return updated

    async def confirm_schedule(self, schedule_id: str) -> dict:
        schedule = await self.repository.get_by_id(schedule_id)
        if not schedule:
            raise ScheduleServiceError("Schedule not found")
        confirm_update = ScheduleUpdate(status="confirmed")
        updated = await self.repository.update(schedule_id, confirm_update)
        if not updated:
            raise ScheduleServiceError("Failed to confirm schedule")
        return updated

    async def complete_schedule(self, schedule_id: str) -> dict:
        schedule = await self.repository.get_by_id(schedule_id)
        if not schedule:
            raise ScheduleServiceError("Schedule not found")
        complete_update = ScheduleUpdate(status="completed")
        updated = await self.repository.update(schedule_id, complete_update)
        if not updated:
            raise ScheduleServiceError("Failed to complete schedule")
        return updated
