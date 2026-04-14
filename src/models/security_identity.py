from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class AllowedEndpoint(BaseModel):
    """Endpoint permitido para acesso."""

    method: str = Field(..., description="Método HTTP permitido")
    path: str = Field(..., description="Caminho permitido (pode conter wildcards)")


class AccessControl(BaseModel):
    """Regras de controle de acesso da identidade de segurança."""

    type: str = Field(..., description="Tipo de controle de acesso")
    allowed_endpoints: List[AllowedEndpoint] = Field(
        default_factory=list, description="Lista de endpoints permitidos"
    )
    allowed_mcp_servers: List[str] = Field(
        default_factory=list, description="Lista de servidores MCP permitidos"
    )


class Credentials(BaseModel):
    """Credenciais da identidade de segurança."""

    client_id: str = Field(..., description="Identificador único do cliente")
    client_secret: str = Field(..., description="Segredo do cliente")


class SecurityIdentityCreate(BaseModel):
    """Modelo para criação de uma identidade de segurança."""

    app_name: str = Field(..., description="Nome da aplicação/identidade")
    credentials: Credentials = Field(..., description="Credenciais de acesso")
    access_control: AccessControl = Field(..., description="Regras de controle de acesso")
    is_active: bool = Field(default=True, description="Se a identidade está ativa")


class SecurityIdentityOut(BaseModel):
    """Modelo de saída de uma identidade de segurança persistida."""

    id: str = Field(..., alias="id")
    app_name: str
    credentials: Credentials
    access_control: AccessControl
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}
