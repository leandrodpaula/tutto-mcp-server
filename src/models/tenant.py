from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from src.models.pyobjectid import PyObjectId

class TenantCreate(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Tutto Barbershop"})
    document: str = Field(..., json_schema_extra={"example": "12.345.678/0001-90"})
    phone: str = Field(..., json_schema_extra={"example": "5511999999999"})
    domain: Optional[str] = Field(None, json_schema_extra={"example": "tutto.barbershop.com"})
    token: Optional[str] = Field(None, json_schema_extra={"example": "random-auth-token"})

class TenantOut(BaseModel):
    id: PyObjectId = Field(..., alias="id")
    name: str
    document: str
    phone: str
    domain: Optional[str]
    token: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
