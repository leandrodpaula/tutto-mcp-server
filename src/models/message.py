from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from src.models.pyobjectid import PyObjectId


class MessageCreate(BaseModel):
    tenant_id: str
    customer_id: str
    type: str
    author: Literal["system", "user"]
    content: str


class MessageOut(BaseModel):
    id: PyObjectId = Field(..., alias="id")
    tenant_id: str
    customer_id: str
    type: str
    author: str
    content: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
