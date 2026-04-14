"""Rotas HTTP para mensagens."""

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.api.deps import get_db
from src.core.logging import get_logger
from src.models.message import MessageCreate
from src.repositories.message_repository import MessageRepository
from src.services.message_service import MessageService

logger = get_logger(__name__)
router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/pending", status_code=status.HTTP_201_CREATED)
async def create_pending_message(
    payload: MessageCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),  # noqa: B008
) -> dict:
    """Recebe uma mensagem via HTTP e a insere com status 'pending'."""
    try:
        repo = MessageRepository(db)
        service = MessageService(repo)
        message_out = await service.create_message(payload)
        return {
            "id": message_out["id"],
            "status": message_out["status"],
            "created_at": (
                message_out["created_at"].isoformat()
                if hasattr(message_out["created_at"], "isoformat")
                else message_out["created_at"]
            ),
        }
    except Exception as e:
        logger.error(f"Error creating pending message via HTTP: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
