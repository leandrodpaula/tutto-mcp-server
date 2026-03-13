from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime
from src.models.pyobjectid import PyObjectId

class SessionData(BaseModel):
    type: str = Field(..., json_schema_extra={"example": "text"})
    content: str = Field(..., json_schema_extra={"example": "Olá, como posso ajudar?"})

class SessionCreate(BaseModel):
    tenant_id: str = Field(..., json_schema_extra={"example": "65f1a2b3c4d5e6f7a8b9c0d1"})
    user_id: str = Field(..., json_schema_extra={"example": "65f1a2b3c4d5e6f7a8b9c0d2"})
    session_id: str = Field(..., json_schema_extra={"example": "session_123"})
    author: Literal["user", "agent"] = Field(..., json_schema_extra={"example": "agent"})
    session: SessionData

class SessionOut(BaseModel):
    id: PyObjectId = Field(..., alias="id")
    tenant_id: str
    user_id: str
    session_id: str
    author: str
    session: SessionData
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
