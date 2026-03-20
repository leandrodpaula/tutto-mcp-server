from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime
from src.models.pyobjectid import PyObjectId

class SubscriptionCreate(BaseModel):
    tenant_id: str = Field(..., json_schema_extra={"example": "65f1a2b3c4d5e6f7a8b9c0d1"})
    plan: str = Field(..., json_schema_extra={"example": "basic"})
    status: Literal["active", "inactive", "cancelled", "expired"] = Field(
        "active", json_schema_extra={"example": "active"}
    )
    type: Literal["monthly", "annual"] = Field("monthly", json_schema_extra={"example": "monthly"})
    starts_at: Optional[datetime] = Field(None, json_schema_extra={"example": "2026-03-18T00:00:00"})
    expires_at: Optional[datetime] = Field(None, json_schema_extra={"example": "2026-04-18T00:00:00"})
    coupon: Optional[str] = Field(None, json_schema_extra={"example": "TUTTO30"})
    is_free: bool = Field(False, json_schema_extra={"example": False})

class SubscriptionUpdate(BaseModel):
    plan: Optional[str] = Field(None, json_schema_extra={"example": "premium"})
    status: Optional[Literal["active", "inactive", "cancelled", "expired"]] = Field(
        None, json_schema_extra={"example": "active"}
    )
    type: Optional[Literal["monthly", "annual"]] = Field(None, json_schema_extra={"example": "monthly"})
    expires_at: Optional[datetime] = Field(None, json_schema_extra={"example": "2026-05-18T00:00:00"})
    is_free: Optional[bool] = Field(None, json_schema_extra={"example": True})
    cancel_reason: Optional[str] = Field(None, json_schema_extra={"example": "Customer requested"})

class SubscriptionOut(BaseModel):
    id: PyObjectId = Field(..., alias="id")
    tenant_id: str
    plan: str
    status: str
    type: Literal["monthly", "annual"] = "monthly"
    starts_at: Optional[datetime]
    expires_at: Optional[datetime]
    coupon: Optional[str]
    is_free: bool = False
    cancel_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
