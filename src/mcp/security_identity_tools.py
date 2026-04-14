from typing import List, Optional

from fastmcp import FastMCP

from src.core.database import get_database
from src.core.logging import get_logger
from src.repositories.security_identity_repository import SecurityIdentityRepository
from src.services.auth_service import AuthService, AuthServiceError

logger = get_logger(__name__)


def register_security_identity_tools(mcp: FastMCP) -> None:
    """Registra as tools de gerenciamento de identidades de segurança."""

    @mcp.tool()
    async def create_security_identity(
        client_id: str,
        client_secret: str,
        name: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        enabled: bool = True,
    ) -> str:
        """Cria uma nova identidade de segurança (client_id/client_secret) no MongoDB.

        Args:
            client_id: Identificador único do cliente.
            client_secret: Segredo do cliente.
            name: Nome descritivo (opcional).
            scopes: Lista de permissões/escopos (opcional).
            enabled: Se a identidade está ativa (padrão: True).

        Returns:
            Mensagem de confirmação com o ID criado.
        """
        try:
            db = get_database()
            repo = SecurityIdentityRepository(db)
            identity = await repo.create_identity(
                client_id=client_id,
                client_secret=client_secret,
                name=name,
                scopes=scopes or [],
                enabled=enabled,
            )
            return (
                f"Security identity created successfully."
                f" ID: {identity['id']}, client_id: {client_id}"
            )
        except Exception as exc:
            logger.error(f"Error creating security identity: {exc}")
            raise

    @mcp.tool()
    async def validate_security_identity(client_id: str, client_secret: str) -> str:
        """Valida um par client_id/client_secret contra o MongoDB.

        Args:
            client_id: Identificador do cliente.
            client_secret: Segredo do cliente.

        Returns:
            Mensagem confirmando que as credenciais são válidas.
        """
        try:
            db = get_database()
            service = AuthService(db)
            await service.authenticate(client_id=client_id, client_secret=client_secret)
            return f"Credentials for client_id '{client_id}' are valid."
        except AuthServiceError as exc:
            logger.warning(f"Validation failed for {client_id}: {exc}")
            raise
