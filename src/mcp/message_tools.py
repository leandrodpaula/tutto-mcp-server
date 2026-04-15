from typing import Literal

from fastmcp import FastMCP

from src.core.database import get_database
from src.core.logging import get_logger
from src.models.message import MessageCreate
from src.repositories.message_repository import MessageRepository
from src.services.message_service import MessageService

logger = get_logger(__name__)


def register_message_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    async def create_pending_message(
        tenant_id: str, customer_id: str, type: str, author: Literal["system", "user"], content: str
    ) -> str:
        """
        Adiciona uma nova mensagem ao banco de dados com o status de
        'pending' para ser processada depois.

        Args:
            tenant_id: O ID do tenant.
            customer_id: O ID do cliente.
            type: O tipo de mensagem (text, img, video, audio).
            author: O autor da mensagem (system ou user).
            content: O conteúdo da mensagem em texto.
        """
        if type not in ["text", "img", "video", "audio"]:
            logger.warning(
                f"Warning: Message type '{type}' is not one of the standard types "
                f"[text, img, video, audio]."
            )

        try:
            db = get_database()
            repo = MessageRepository(db)
            service = MessageService(repo)

            message_in = MessageCreate(
                tenant_id=tenant_id,
                customer_id=customer_id,
                type=type,
                author=author,
                content=content,
            )

            message_out = await service.create_message(message_in)
            return (
                f"Mensagem enviada com sucesso e está pendente de processamento. "
                f"ID: {message_out['id']}"
            )
        except Exception as e:
            logger.error(f"Error creating pending message for customer {customer_id}: {str(e)}")
            raise
