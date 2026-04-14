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
        app_name: str,
        client_id: str,
        client_secret: str,
        access_control_type: str,
        allowed_endpoints: Optional[List[str]] = None,
        allowed_mcp_servers: Optional[List[str]] = None,
        is_active: bool = True,
    ) -> str:
        """Cria uma nova identidade de segurança no MongoDB.

        Args:
            app_name: Nome da aplicação/identidade.
            client_id: Identificador único do cliente.
            client_secret: Segredo do cliente.
            access_control_type: Tipo de controle de acesso (ex: WEBHOOK_HANDLER).
            allowed_endpoints: Lista de endpoints permitidos no formato "METHOD /path".
            allowed_mcp_servers: Lista de servidores MCP permitidos.
            is_active: Se a identidade está ativa (padrão: True).

        Returns:
            Mensagem de confirmação com o ID criado.
        """
        try:
            endpoints = []
            for endpoint in allowed_endpoints or []:
                parts = endpoint.split(" ", 1)
                if len(parts) == 2:
                    endpoints.append({"method": parts[0], "path": parts[1]})

            credentials = {"client_id": client_id, "client_secret": client_secret}
            access_control = {
                "type": access_control_type,
                "allowed_endpoints": endpoints,
                "allowed_mcp_servers": allowed_mcp_servers or [],
            }

            db = get_database()
            repo = SecurityIdentityRepository(db)
            identity = await repo.create_identity(
                app_name=app_name,
                credentials=credentials,
                access_control=access_control,
                is_active=is_active,
            )
            return (
                f"Security identity created successfully."
                f" ID: {identity['id']}, app_name: {app_name}"
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
