from typing import List, Optional

from fastmcp import FastMCP

from src.core.database import get_database
from src.core.logging import get_logger

logger = get_logger(__name__)
from src.models.plan import PlanCreate, PlanUpdate
from src.repositories.plan_repository import PlanRepository
from src.services.plan_service import PlanService


def register_plan_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    async def create_plan(
        name: str,
        title: str,
        description: str,
        price: float,
        is_active: bool = True,
        features: Optional[List[str]] = None,
    ) -> str:
        """
        Creates a new subscription plan.

        Args:
            name: The internal name of the plan (e.g., 'basic').
            title: The display title (e.g., 'Plano Básico').
            description: Description of the plan features.
            price: The monthly price in BRL.
            is_active: Whether the plan is available for new subscriptions.
            features: A list of features included in the plan.
        """
        try:
            db = get_database()
            repo = PlanRepository(db)
            service = PlanService(repo)
            plan_in = PlanCreate(
                name=name,
                title=title,
                description=description,
                price=price,
                is_active=is_active,
                features=features or [],
            )
            created = await service.create_plan(plan_in)
            return f"Plan created successfully: {created}"
        except Exception as e:
            logger.error(f"Error creating plan: {str(e)}")
            raise

    @mcp.tool()
    async def list_active_plans() -> str:
        """Lists all currently active subscription plans."""
        try:
            db = get_database()
            repo = PlanRepository(db)
            service = PlanService(repo)
            plans = await service.list_active_plans()
            return f"Active plans: {plans}"
        except Exception as e:
            logger.error(f"Error listing plans: {str(e)}")
            raise

    @mcp.tool()
    async def update_plan(
        plan_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        is_active: Optional[bool] = None,
        change_reason: Optional[str] = None,
        features: Optional[List[str]] = None,
    ) -> str:
        """Updates an existing subscription plan."""
        try:
            db = get_database()
            repo = PlanRepository(db)
            service = PlanService(repo)
            update_in = PlanUpdate(
                title=title,
                description=description,
                price=price,
                is_active=is_active,
                change_reason=change_reason,
                features=features,
            )
            plan_out = await service.update_plan(plan_id, update_in)
            return f"Plan updated successfully: {plan_out}"
        except Exception as e:
            logger.error(f"Error updating plan: {str(e)}")
            raise
