from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from src.models.pyobjectid import PyObjectId


class MessageData(BaseModel):
    type: str = Field(..., json_schema_extra={"example": "text"})
    content: str = Field(..., json_schema_extra={"example": "Olá, como posso ajudar?"})


class SessionCreate(BaseModel):
    tenant_id: str = Field(..., json_schema_extra={"example": "65f1a2b3c4d5e6f7a8b9c0d1"})
    user_id: str = Field(..., json_schema_extra={"example": "65f1a2b3c4d5e6f7a8b9c0d2"})
    session_id: Optional[str] = Field(None, json_schema_extra={"example": "session_123"})
    author: Literal["user", "agent"] = Field(..., json_schema_extra={"example": "agent"})
    message: MessageData


class SessionOut(BaseModel):
    id: PyObjectId = Field(..., alias="id")
    tenant_id: str
    user_id: str
    session_id: str
    author: str
    message: MessageData
    created_at: datetime
    expires_at: datetime
    is_active: bool
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
