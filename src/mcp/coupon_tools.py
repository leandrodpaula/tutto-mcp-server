from fastmcp import FastMCP
from typing import Optional
from src.core.database import get_database
from src.repositories.coupon_repository import CouponRepository
from src.services.coupon_service import CouponService, CouponServiceError
from src.models.coupon import CouponCreate, CouponUpdate
from datetime import datetime

def register_coupon_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    async def create_coupon(
        title: str,
        short_code: str,
        ttl: int,
        description: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        is_active: bool = True,
    ) -> str:
        """
        Creates a new promotional coupon.

        Args:
            title: The title of the coupon.
            short_code: The unique code (e.g., TUTTO30).
            ttl: Duration in days.
            description: Optional description.
            start_date: Start date in ISO format (optional, defaults to now).
            end_date: End date in ISO format (optional).
            is_active: Whether the coupon is active (default: True).
        """
        try:
            db = get_database()
            repo = CouponRepository(db)
            service = CouponService(repo)

            parsed_start = datetime.fromisoformat(start_date) if start_date else datetime.utcnow()
            parsed_end = datetime.fromisoformat(end_date) if end_date else None

            coupon_in = CouponCreate(
                title=title,
                short_code=short_code,
                ttl=ttl,
                description=description,
                start_date=parsed_start,
                end_date=parsed_end,
                is_active=is_active
            )
            coupon_out = await service.create_coupon(coupon_in)
            return f"Coupon created successfully: {coupon_out}"
        except CouponServiceError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def get_coupon(short_code: str) -> str:
        """Retrieves a coupon by its short code."""
        try:
            db = get_database()
            repo = CouponRepository(db)
            service = CouponService(repo)
            coupon = await service.get_coupon_by_code(short_code)
            return f"Coupon found: {coupon}"
        except CouponServiceError as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def list_active_coupons() -> str:
        """Lists all currently active coupons."""
        try:
            db = get_database()
            repo = CouponRepository(db)
            service = CouponService(repo)
            coupons = await service.list_active_coupons()
            return f"Active coupons: {coupons}"
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def update_coupon(
        coupon_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        ttl: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> str:
        """Updates an existing coupon."""
        try:
            db = get_database()
            repo = CouponRepository(db)
            service = CouponService(repo)
            update_in = CouponUpdate(
                title=title,
                description=description,
                ttl=ttl,
                is_active=is_active
            )
            coupon_out = await service.update_coupon(coupon_id, update_in)
            return f"Coupon updated successfully: {coupon_out}"
        except CouponServiceError as e:
            return f"Error: {str(e)}"
