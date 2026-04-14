from motor.motor_asyncio import AsyncIOMotorDatabase

from src.repositories.security_identity_repository import SecurityIdentityRepository


class AuthServiceError(Exception):
    """Exceção customizada para erros de autenticação."""

    pass


class AuthService:
    """Serviço de autenticação baseado em client_id e client_secret."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = SecurityIdentityRepository(db)

    async def authenticate(self, client_id: str, client_secret: str) -> dict:
        """Valida client_id e client_secret contra o MongoDB.

        Args:
            client_id: Identificador do cliente.
            client_secret: Segredo do cliente.

        Returns:
            Documento da identidade autenticada.

        Raises:
            AuthServiceError: Se as credenciais forem inválidas ou a identidade estiver desativada.
        """
        identity = await self.repo.find_by_client_id(client_id)
        if identity is None:
            raise AuthServiceError("Invalid client_id or client_secret")

        if not identity.get("is_active", True):
            raise AuthServiceError("Identity is disabled")

        credentials = identity.get("credentials") or {}
        if credentials.get("client_secret") != client_secret:
            raise AuthServiceError("Invalid client_id or client_secret")

        return identity
