from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime
from src.models.pyobjectid import PyObjectId

class ScheduleCreate(BaseModel):
    tenant_id: str = Field(..., json_schema_extra={"example": "65f1a2b3c4d5e6f7a8b9c0d1"})
    user_id: str = Field(..., json_schema_extra={"example": "65f1a2b3c4d5e6f7a8b9c0d2"})
    instruction_id: str = Field(..., json_schema_extra={"example": "65f1a2b3c4d5e6f7a8b9c0d3"})
    scheduled_at: datetime = Field(..., json_schema_extra={"example": "2026-03-20T14:00:00"})
    notes: Optional[str] = Field(None, json_schema_extra={"example": "Prefiro corte mais curto nas laterais"})

class ScheduleUpdate(BaseModel):
    scheduled_at: Optional[datetime] = Field(None, json_schema_extra={"example": "2026-03-21T10:00:00"})
    status: Optional[Literal["pending", "confirmed", "cancelled", "completed", "no_show"]] = Field(
        None, json_schema_extra={"example": "confirmed"}
    )
    notes: Optional[str] = Field(None, json_schema_extra={"example": "Remarcar para manhã"})

class ScheduleOut(BaseModel):
    id: PyObjectId = Field(..., alias="id")
    tenant_id: str
    user_id: str
    instruction_id: str
    scheduled_at: datetime
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
