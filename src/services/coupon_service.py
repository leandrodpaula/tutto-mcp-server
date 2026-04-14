from datetime import datetime
from typing import List

from src.models.coupon import CouponCreate, CouponUpdate
from src.repositories.coupon_repository import CouponRepository


class CouponServiceError(Exception):
    pass


class CouponService:
    def __init__(self, repository: CouponRepository):
        self.repository = repository

    async def create_coupon(self, coupon: CouponCreate) -> dict:
        existing = await self.repository.get_by_short_code(coupon.short_code)
        if existing:
            raise CouponServiceError(f"Coupon with code {coupon.short_code} already exists")
        return await self.repository.create(coupon)

    async def validate_coupon(self, short_code: str) -> dict:
        """
        Validates if a coupon exists, is active, and within date range.
        Returns the coupon dict if valid, raises error otherwise.
        """
        coupon = await self.repository.get_by_short_code(short_code)
        if not coupon:
            raise CouponServiceError(f"Coupon {short_code} not found")

        if not coupon.get("is_active"):
            raise CouponServiceError(f"Coupon {short_code} is inactive")

        now = datetime.utcnow()
        if coupon.get("start_date") > now:
            raise CouponServiceError(f"Coupon {short_code} is not yet valid")

        if coupon.get("end_date") and coupon.get("end_date") < now:
            raise CouponServiceError(f"Coupon {short_code} has expired")

        return coupon

    async def get_coupon(self, coupon_id: str) -> dict:
        coupon = await self.repository.get_by_id(coupon_id)
        if not coupon:
            raise CouponServiceError("Coupon not found")
        return coupon

    async def get_coupon_by_code(self, short_code: str) -> dict:
        coupon = await self.repository.get_by_short_code(short_code)
        if not coupon:
            raise CouponServiceError(f"Coupon {short_code} not found")
        return coupon

    async def list_active_coupons(self) -> List[dict]:
        return await self.repository.list_active()

    async def update_coupon(self, coupon_id: str, coupon_update: CouponUpdate) -> dict:
        updated = await self.repository.update(coupon_id, coupon_update)
        if not updated:
            raise CouponServiceError("Coupon not found or update failed")
        return updated
