from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from src.models.pyobjectid import PyObjectId


class CustomerCreate(BaseModel):
    tenant_id: str = Field(..., json_schema_extra={"example": "65f1a2b3c4d5e6f7a8b9c0d1"})
    name: str = Field(..., json_schema_extra={"example": "Maria Oliveira"})
    email: str = Field(..., json_schema_extra={"example": "maria@example.com"})
    phone: str = Field(..., json_schema_extra={"example": "5511999999999"})
    google_id: Optional[str] = Field(None, json_schema_extra={"example": "123456789"})


class GoogleTokenRequest(BaseModel):
    google_token: str = Field(..., description="ID token JWT recebido do Google")


class CustomerOut(BaseModel):
    id: PyObjectId = Field(..., alias="id")
    tenant_id: str
    name: str
    email: str
    phone: str
    google_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
