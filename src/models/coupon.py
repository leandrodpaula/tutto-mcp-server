from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from src.models.pyobjectid import PyObjectId

class CouponCreate(BaseModel):
    title: str = Field(..., json_schema_extra={"example": "Incentivo Inicial"})
    short_code: str = Field(..., json_schema_extra={"example": "TUTTO30"})
    description: Optional[str] = Field(None, json_schema_extra={"example": "30 dias gratuitos para novos tenants"})
    ttl: int = Field(..., json_schema_extra={"example": 30})
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = Field(None)
    is_active: bool = Field(True)

class CouponUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    ttl: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class CouponOut(BaseModel):
    id: PyObjectId = Field(..., alias="id")
    title: str
    short_code: str
    description: Optional[str]
    ttl: int
    start_date: datetime
    end_date: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
