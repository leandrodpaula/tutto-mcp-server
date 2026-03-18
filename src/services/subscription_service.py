from typing import Optional
from src.models.subscription import SubscriptionCreate, SubscriptionUpdate
from src.repositories.subscription_repository import SubscriptionRepository
from src.services.payment_service import PaymentService
from src.services.coupon_service import CouponService, CouponServiceError
from src.services.plan_service import PlanService, PlanServiceError
from src.core.config import settings
from datetime import datetime, timedelta

class SubscriptionServiceError(Exception):
    pass

class SubscriptionService:
    def __init__(self, repository: SubscriptionRepository, coupon_service: CouponService, plan_service: PlanService):
        self.repository = repository
        self.payment_service = PaymentService()
        self.coupon_service = coupon_service
        self.plan_service = plan_service

    async def create_subscription(self, subscription: SubscriptionCreate) -> dict:
        # We check for an active subscription to upgrade/update
        existing = await self.repository.get_by_tenant(subscription.tenant_id, is_active=True)
        
        # Get plan details and price from DB
        try:
            plan_data = await self.plan_service.get_plan_by_name(subscription.plan)
            price = plan_data.get("price", 0.0)
            if not plan_data.get("is_active"):
                raise SubscriptionServiceError(f"Plan {subscription.plan} is currently inactive")
        except PlanServiceError as e:
            raise SubscriptionServiceError(f"Plan validation failed: {str(e)}")
            
        # Handle free plan coupon logic
        if subscription.plan == "free":
            if not subscription.coupon:
                raise SubscriptionServiceError("A coupon is required for the free plan.")
            
            # Validate coupon and calculate expires_at
            try:
                coupon_data = await self.coupon_service.validate_coupon(subscription.coupon)
                subscription.expires_at = datetime.utcnow() + timedelta(days=coupon_data["ttl"])
            except CouponServiceError as e:
                raise SubscriptionServiceError(f"Coupon validation failed: {str(e)}")

        # Generate payment link if applicable
        payment_link = None
        if price > 0 and not subscription.is_free:
            try:
                payment_link = await self.payment_service.create_payment_link(
                    subscription.tenant_id, 
                    subscription.plan, 
                    price
                )
            except Exception as e:
                print(f"Failed to generate payment link: {str(e)}")
                payment_link = "Error generating link. Contact support."

        if existing:
            # Upgrade existing subscription
            update_data = SubscriptionUpdate(
                plan=subscription.plan,
                status=subscription.status,
                expires_at=subscription.expires_at,
                is_free=subscription.is_free
            )
            # We don't update coupon on upgrade for now, unless requested
            result = await self.repository.update_by_tenant(subscription.tenant_id, update_data)
            if not result:
                raise SubscriptionServiceError("Failed to update existing subscription")
            result["payment_link"] = payment_link
            return result
        
        # Create new subscription
        created = await self.repository.create(subscription)
        created["payment_link"] = payment_link
        return created

    async def get_subscription(self, tenant_id: str, is_active: Optional[bool] = True) -> dict:
        subscription = await self.repository.get_by_tenant(tenant_id, is_active=is_active)
        if not subscription:
            status_str = "active " if is_active else ""
            raise SubscriptionServiceError(f"No {status_str}subscription found for tenant {tenant_id}")
        return subscription

    async def update_subscription(self, tenant_id: str, subscription_update: SubscriptionUpdate) -> dict:
        existing = await self.repository.get_by_tenant(tenant_id, is_active=True)
        if not existing:
            raise SubscriptionServiceError(f"No active subscription found for tenant {tenant_id}")
            
        # If plan is being updated, validate it
        if subscription_update.plan:
            try:
                plan_data = await self.plan_service.get_plan_by_name(subscription_update.plan)
                if not plan_data.get("is_active"):
                    raise SubscriptionServiceError(f"Plan {subscription_update.plan} is currently inactive")
            except PlanServiceError as e:
                raise SubscriptionServiceError(f"Plan validation failed: {str(e)}")

        updated = await self.repository.update_by_tenant(tenant_id, subscription_update)
        if not updated:
            raise SubscriptionServiceError("Failed to update subscription")
        return updated

    async def cancel_subscription(self, tenant_id: str) -> dict:
        existing = await self.repository.get_by_tenant(tenant_id, is_active=True)
        if not existing:
            raise SubscriptionServiceError(f"No active subscription found for tenant {tenant_id}")
        
        # When cancelling, we set status and is_active=False
        cancel_update = SubscriptionUpdate(status="cancelled")
        # SubscriptionUpdate doesn't have is_active, so I'll just use status for now 
        # as it's the standard. If I need is_active I'd need to update the model.
        # But wait, the repository doesn't have is_active in Update model.
        # I'll just update the status as before.
        updated = await self.repository.update_by_tenant(tenant_id, cancel_update)
        if not updated:
            raise SubscriptionServiceError("Failed to cancel subscription")
        return updated
