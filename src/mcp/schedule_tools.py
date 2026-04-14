from fastmcp import FastMCP
from typing import Optional, Literal
from datetime import datetime
from src.core.database import get_database
from src.core.logging import get_logger

logger = get_logger(__name__)
from src.repositories.schedule_repository import ScheduleRepository
from src.services.schedule_service import ScheduleService, ScheduleServiceError
from src.models.schedule import ScheduleCreate, ScheduleUpdate


def register_schedule_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    async def create_schedule(
        tenant_id: str,
        user_id: str,
        instruction_id: str,
        scheduled_at: str,
        notes: Optional[str] = None,
    ) -> str:
        """
        Creates a new schedule (appointment) for a user with a tenant service.

        Args:
            tenant_id: The ID of the tenant.
            user_id: The ID of the user booking the service.
            instruction_id: The ID of the service/instruction being booked.
            scheduled_at: The appointment date and time in ISO format (e.g., '2026-03-20T14:00:00').
            notes: Optional notes from the user about the appointment.

        Returns:
            A string with the created schedule details or error message.
        """
        try:
            db = get_database()
            repo = ScheduleRepository(db)
            service = ScheduleService(repo)

            parsed_dt = datetime.fromisoformat(scheduled_at)
            schedule_in = ScheduleCreate(
                tenant_id=tenant_id,
                user_id=user_id,
                instruction_id=instruction_id,
                scheduled_at=parsed_dt,
                notes=notes,
            )
            schedule_out = await service.create_schedule(schedule_in)
            return f"Schedule created successfully: {schedule_out}"
        except Exception as e:
            logger.error(f"Error creating schedule for tenant {tenant_id}: {str(e)}")
            raise

    @mcp.tool()
    async def get_schedule(schedule_id: str) -> str:
        """
        Retrieves a schedule by its ID.

        Args:
            schedule_id: The ID of the schedule.

        Returns:
            A string with the schedule details or error message.
        """
        try:
            db = get_database()
            repo = ScheduleRepository(db)
            service = ScheduleService(repo)

            schedule_out = await service.get_schedule(schedule_id)
            return f"Schedule found: {schedule_out}"
        except Exception as e:
            logger.error(f"Error getting schedule {schedule_id}: {str(e)}")
            raise

    @mcp.tool()
    async def list_schedules(
        tenant_id: str,
        status: Optional[
            Literal["pending", "confirmed", "cancelled", "completed", "no_show"]
        ] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> str:
        """
        Lists schedules for a tenant with optional filters.

        Args:
            tenant_id: The ID of the tenant.
            status: Filter by status (optional).
            date_from: Filter from this date in ISO format (optional).
            date_to: Filter up to this date in ISO format (optional).

        Returns:
            A string with the list of schedules or error message.
        """
        try:
            db = get_database()
            repo = ScheduleRepository(db)
            service = ScheduleService(repo)

            filters = {}
            if status:
                filters["status"] = status
            if date_from:
                filters["date_from"] = datetime.fromisoformat(date_from)
            if date_to:
                filters["date_to"] = datetime.fromisoformat(date_to)

            schedules = await service.list_schedules(tenant_id, filters if filters else None)
            if not schedules:
                return f"No schedules found for tenant {tenant_id}"
            return f"Schedules for tenant {tenant_id}: {schedules}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def list_user_schedules(tenant_id: str, user_id: str) -> str:
        """
        Lists all schedules for a specific user within a tenant.

        Args:
            tenant_id: The ID of the tenant.
            user_id: The ID of the user.

        Returns:
            A string with the list of user schedules or error message.
        """
        try:
            db = get_database()
            repo = ScheduleRepository(db)
            service = ScheduleService(repo)

            schedules = await service.list_user_schedules(tenant_id, user_id)
            if not schedules:
                return f"No schedules found for user {user_id}"
            return f"Schedules for user {user_id}: {schedules}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def update_schedule(
        schedule_id: str,
        scheduled_at: Optional[str] = None,
        status: Optional[
            Literal["pending", "confirmed", "cancelled", "completed", "no_show"]
        ] = None,
        notes: Optional[str] = None,
    ) -> str:
        """
        Updates an existing schedule.

        Args:
            schedule_id: The ID of the schedule to update.
            scheduled_at: The new date/time in ISO format (optional).
            status: The new status (optional).
            notes: Updated notes (optional).

        Returns:
            A string with the updated schedule details or error message.
        """
        try:
            db = get_database()
            repo = ScheduleRepository(db)
            service = ScheduleService(repo)

            parsed_dt = datetime.fromisoformat(scheduled_at) if scheduled_at else None
            schedule_update = ScheduleUpdate(
                scheduled_at=parsed_dt,
                status=status,
                notes=notes,
            )
            schedule_out = await service.update_schedule(schedule_id, schedule_update)
            return f"Schedule updated successfully: {schedule_out}"
        except Exception as e:
            logger.error(f"Error updating schedule {schedule_id}: {str(e)}")
            raise

    @mcp.tool()
    async def cancel_schedule(schedule_id: str) -> str:
        """
        Cancels a schedule by setting its status to 'cancelled'.

        Args:
            schedule_id: The ID of the schedule to cancel.

        Returns:
            A string confirming the cancellation or error message.
        """
        try:
            db = get_database()
            repo = ScheduleRepository(db)
            service = ScheduleService(repo)

            schedule_out = await service.cancel_schedule(schedule_id)
            return f"Schedule cancelled successfully: {schedule_out}"
        except Exception as e:
            logger.error(f"Error cancelling schedule {schedule_id}: {str(e)}")
            raise

    @mcp.tool()
    async def confirm_schedule(schedule_id: str) -> str:
        """
        Confirms a schedule by setting its status to 'confirmed'.

        Args:
            schedule_id: The ID of the schedule to confirm.

        Returns:
            A string confirming the action or error message.
        """
        try:
            db = get_database()
            repo = ScheduleRepository(db)
            service = ScheduleService(repo)

            schedule_out = await service.confirm_schedule(schedule_id)
            return f"Schedule confirmed successfully: {schedule_out}"
        except Exception as e:
            logger.error(f"Error confirming schedule {schedule_id}: {str(e)}")
            raise

    @mcp.tool()
    async def complete_schedule(schedule_id: str) -> str:
        """
        Marks a schedule as completed.

        Args:
            schedule_id: The ID of the schedule to complete.

        Returns:
            A string confirming the completion or error message.
        """
        try:
            db = get_database()
            repo = ScheduleRepository(db)
            service = ScheduleService(repo)

            schedule_out = await service.complete_schedule(schedule_id)
            return f"Schedule completed successfully: {schedule_out}"
        except Exception as e:
            logger.error(f"Error completing schedule {schedule_id}: {str(e)}")
            raise
