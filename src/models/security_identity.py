from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SecurityIdentityCreate(BaseModel):
    """Modelo para criação de uma identidade de segurança."""

    client_id: str = Field(..., description="Identificador único do cliente")
    client_secret: str = Field(..., description="Segredo do cliente")
    name: Optional[str] = Field(default=None, description="Nome descritivo da identidade")
    scopes: List[str] = Field(default_factory=list, description="Lista de permissões/escopos")
    enabled: bool = Field(default=True, description="Se a identidade está ativa")


class SecurityIdentityOut(BaseModel):
    """Modelo de saída de uma identidade de segurança persistida."""

    id: str = Field(..., alias="id")
    client_id: str
    name: Optional[str] = None
    scopes: List[str] = Field(default_factory=list)
    enabled: bool
    created_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}
