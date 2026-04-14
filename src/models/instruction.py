from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime
from src.models.pyobjectid import PyObjectId


class InstructionCreate(BaseModel):
    tenant_id: str = Field(..., json_schema_extra={"example": "65f1a2b3c4d5e6f7a8b9c0d1"})
    type: Literal["general", "service", "product"] = Field(
        ..., json_schema_extra={"example": "service"}
    )
    name: str = Field(..., json_schema_extra={"example": "Corte de Cabelo"})
    text: Optional[str] = Field(
        None, json_schema_extra={"example": "Informação geral sobre o estabelecimento"}
    )
    price: Optional[float] = Field(None, json_schema_extra={"example": 50.0})
    duration_minutes: Optional[int] = Field(None, json_schema_extra={"example": 30})
    description: Optional[str] = Field(
        None, json_schema_extra={"example": "Corte clássico com tesoura e máquina"}
    )
    instructions: Optional[str] = Field(
        None, json_schema_extra={"example": "Chegar 5 minutos antes"}
    )


class InstructionOut(BaseModel):
    id: PyObjectId = Field(..., alias="id")
    tenant_id: str
    type: str
    name: str
    text: Optional[str]
    price: Optional[float]
    duration_minutes: Optional[int]
    description: Optional[str]
    instructions: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
