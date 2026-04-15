"""Rota HTTP para receber eventos de webhooks (Evolution API)."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.api.deps import get_db
from src.core.config import settings
from src.core.logging import get_logger
from src.models.webhook_event import WebhookEventPayload
from src.repositories.event_repository import EventRepository

logger = get_logger(__name__)
router = APIRouter(prefix="/webhook", tags=["events"])


@router.post("/events", status_code=status.HTTP_200_OK)
async def receive_webhook_event(
    request: Request,
    payload: WebhookEventPayload,
    db: AsyncIOMotorDatabase = Depends(get_db),  # noqa: B008
) -> dict:
    # Validação mínima de origem via API key no header ou no payload
    api_key = request.headers.get("apikey") or payload.apikey
    if not api_key or api_key != settings.EVOLUTION_API_KEY:
        logger.warning(f"Webhook received with invalid apikey from {request.client.host if request.client else 'unknown'}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    """Recebe eventos de webhook (mensagens, QR code, etc.) e persiste no MongoDB.

    Eventos suportados incluem MESSAGES_UPSERT, QRCODE_UPDATED, CONNECTION_UPDATE,
    e outros eventos emitidos pelo Evolution API.
    """
    try:
        repo = EventRepository(db)
        event = await repo.create_webhook_event(
            event=payload.event,
            instance=payload.instance,
            data=payload.data,
            destination=payload.destination,
            date_time=payload.date_time,
            sender=payload.sender,
            server_url=payload.server_url,
            apikey=payload.apikey,
        )
        logger.info(f"Webhook event saved: {payload.event} for instance {payload.instance}")
        return {
            "status": "ok",
            "event_id": event["id"],
            "event": payload.event,
            "instance": payload.instance,
        }
    except Exception as exc:
        logger.error(f"Error saving webhook event: {exc}")
        # Retorna 200 mesmo em erro interno para evitar retentativas desnecessárias
        # do Evolution API, mas loga o problema.
        return {
            "status": "ignored",
            "detail": str(exc),
        }
