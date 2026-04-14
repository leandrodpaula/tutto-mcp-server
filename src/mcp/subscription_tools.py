from fastmcp import FastMCP
from typing import Optional, Literal
from src.core.database import get_database
from src.core.logging import get_logger

logger = get_logger(__name__)
from src.repositories.subscription_repository import SubscriptionRepository
from src.repositories.tenant_repository import TenantRepository
from src.repositories.coupon_repository import CouponRepository
from src.repositories.plan_repository import PlanRepository
from src.services.subscription_service import SubscriptionService, SubscriptionServiceError
from src.services.coupon_service import CouponService
from src.services.plan_service import PlanService
from src.models.subscription import SubscriptionCreate, SubscriptionUpdate
from datetime import datetime


def register_subscription_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    async def create_subscription(
        tenant_id: str,
        plan: str,
        status: str = "active",
        type: Literal["monthly", "annual"] = "monthly",
        coupon: Optional[str] = None,
        is_free: bool = False,
    ) -> str:
        """
        Creates a new subscription for a tenant.

        Args:
            tenant_id: The ID of the tenant.
            plan: The subscription plan name (e.g., 'silver', 'gold').
            status: Initial status (default: 'active').
            type: Subscription type ('monthly' or 'annual').
            coupon: Optional coupon code.
            is_free: If True, skips payment link generation.
        """
        try:
            db = get_database()
            repo = SubscriptionRepository(db)
            tenant_repo = TenantRepository(db)
            coupon_repo = CouponRepository(db)
            plan_repo = PlanRepository(db)

            coupon_service = CouponService(coupon_repo)
            plan_service = PlanService(plan_repo)
            service = SubscriptionService(repo, tenant_repo, coupon_service, plan_service)

            sub_in = SubscriptionCreate(
                tenant_id=tenant_id,
                plan=plan,
                status=status,
                type=type,
                coupon=coupon,
                is_free=is_free,
            )
            result = await service.create_subscription(sub_in)
            payment_info = (
                f"\nPayment Link: {result.get('payment_link')}"
                if result.get("payment_link")
                else ""
            )
            return f"Subscription created successfully: {result}{payment_info}"
        except Exception as e:
            logger.error(f"Error creating subscription for tenant {tenant_id}: {str(e)}")
            raise

    @mcp.tool()
    async def get_subscription(tenant_id: str, is_active: Optional[bool] = True) -> str:
        """Retrieves the subscription for a tenant."""
        try:
            db = get_database()
            repo = SubscriptionRepository(db)
            tenant_repo = TenantRepository(db)
            coupon_repo = CouponRepository(db)
            plan_repo = PlanRepository(db)

            coupon_service = CouponService(coupon_repo)
            plan_service = PlanService(plan_repo)
            service = SubscriptionService(repo, tenant_repo, coupon_service, plan_service)

            sub_out = await service.get_subscription(tenant_id, is_active)
            return f"Subscription found: {sub_out}"
        except Exception as e:
            logger.error(f"Error getting subscription for tenant {tenant_id}: {str(e)}")
            raise

    @mcp.tool()
    async def update_subscription(
        tenant_id: str,
        plan: Optional[str] = None,
        status: Optional[str] = None,
        type: Optional[Literal["monthly", "annual"]] = None,
        is_free: Optional[bool] = None,
    ) -> str:
        """
        Updates an existing subscription.

        Args:
            tenant_id: The ID of the tenant.
            plan: New plan name (optional).
            status: New status (optional).
            type: New subscription type (optional, 'monthly' or 'annual').
            is_free: Optional boolean flag.
        """
        try:
            db = get_database()
            repo = SubscriptionRepository(db)
            tenant_repo = TenantRepository(db)
            coupon_repo = CouponRepository(db)
            plan_repo = PlanRepository(db)

            coupon_service = CouponService(coupon_repo)
            plan_service = PlanService(plan_repo)
            service = SubscriptionService(repo, tenant_repo, coupon_service, plan_service)

            update_in = SubscriptionUpdate(plan=plan, status=status, type=type, is_free=is_free)
            result = await service.update_subscription(tenant_id, update_in)
            return f"Subscription updated successfully: {result}"
        except Exception as e:
            logger.error(f"Error updating subscription for tenant {tenant_id}: {str(e)}")
            raise

    @mcp.tool()
    async def cancel_subscription(tenant_id: str, reason: Optional[str] = None) -> str:
        """
        Cancels a subscription.

        Args:
            tenant_id: The ID of the tenant.
            reason: Optional reason for cancellation.
        """
        try:
            db = get_database()
            repo = SubscriptionRepository(db)
            tenant_repo = TenantRepository(db)
            coupon_repo = CouponRepository(db)
            plan_repo = PlanRepository(db)

            coupon_service = CouponService(coupon_repo)
            plan_service = PlanService(plan_repo)
            service = SubscriptionService(repo, tenant_repo, coupon_service, plan_service)

            result = await service.cancel_subscription(tenant_id, reason)
            return f"Subscription cancelled successfully: {result}"
        except Exception as e:
            logger.error(f"Error cancelling subscription for tenant {tenant_id}: {str(e)}")
            raise
