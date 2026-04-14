from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from src.models.pyobjectid import PyObjectId


class PriceHistory(BaseModel):
    price: float
    changed_at: datetime
    reason: Optional[str] = None


class PlanCreate(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "basic"})
    title: str = Field(..., json_schema_extra={"example": "Plano Básico"})
    description: Optional[str] = Field(
        None, json_schema_extra={"example": "Acesso a recursos essenciais"}
    )
    price: float = Field(..., json_schema_extra={"example": 29.90})
    is_active: bool = Field(True)
    features: List[str] = Field(default_factory=list)


class PlanUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None
    change_reason: Optional[str] = None
    features: Optional[List[str]] = None


class PlanOut(BaseModel):
    id: PyObjectId = Field(..., alias="id")
    name: str
    title: str
    description: Optional[str]
    price: float
    price_history: List[PriceHistory] = Field(default_factory=list)
    is_active: bool
    features: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
