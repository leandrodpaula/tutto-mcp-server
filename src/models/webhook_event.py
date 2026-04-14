from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class WebhookEventPayload(BaseModel):
    """Payload genérico enviado pelo Evolution API para webhooks."""

    event: str = Field(..., description="Nome do evento, ex: MESSAGES_UPSERT, QRCODE_UPDATED")
    instance: str = Field(..., description="Nome da instância do WhatsApp")
    data: Any = Field(default=None, description="Dados específicos do evento")
    destination: Optional[str] = Field(default=None, description="URL de destino do webhook")
    date_time: Optional[str] = Field(default=None, description="Data/hora do evento no Evolution")
    sender: Optional[str] = Field(default=None, description="Remetente do evento")
    server_url: Optional[str] = Field(default=None, description="URL do servidor Evolution")
    apikey: Optional[str] = Field(default=None, description="API key da instância")


class WebhookEventOut(BaseModel):
    """Representação de um evento de webhook salvo no MongoDB."""

    id: str = Field(..., alias="id")
    event: str
    instance: str
    data: Any
    destination: Optional[str] = None
    date_time: Optional[str] = None
    sender: Optional[str] = None
    server_url: Optional[str] = None
    received_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}
