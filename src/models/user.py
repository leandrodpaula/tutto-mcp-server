from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from src.models.pyobjectid import PyObjectId

class UserCreate(BaseModel):
    tenant_id: str = Field(..., json_schema_extra={"example": "65f1a2b3c4d5e6f7a8b9c0d1"})
    phone: str = Field(..., json_schema_extra={"example": "5511999999999"})
    nome: str = Field(..., json_schema_extra={"example": "João Silva"})
    email: Optional[str] = Field(None, json_schema_extra={"example": "joao.silva@example.com"})

class UserUpdate(BaseModel):
    phone: Optional[str] = Field(None, json_schema_extra={"example": "5511888888888"})
    nome: Optional[str] = Field(None, json_schema_extra={"example": "João da Silva"})
    email: Optional[str] = Field(None, json_schema_extra={"example": "joao.s@example.com"})

class UserOut(BaseModel):
    id: PyObjectId = Field(..., alias="id")
    tenant_id: str
    phone: str
    nome: str
    email: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
