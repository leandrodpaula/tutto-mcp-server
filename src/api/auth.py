"""Dependências de autenticação para a API HTTP."""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from src.core.database import get_database
from src.core.logging import get_logger
from src.services.auth_service import AuthService, AuthServiceError

logger = get_logger(__name__)
security = HTTPBasic(auto_error=False)


async def require_auth(
    credentials: Optional[HTTPBasicCredentials] = Depends(security),  # noqa: B008
) -> dict:
    """Dependency que exige autenticação via Basic Auth (client_id:client_secret).

    Raises:
        HTTPException: 401 se as credenciais forem inválidas ou ausentes.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Basic"},
        )

    db = get_database()
    service = AuthService(db)
    try:
        identity = await service.authenticate(
            client_id=credentials.username,
            client_secret=credentials.password,
        )
        return identity
    except AuthServiceError as exc:
        logger.warning(f"Authentication failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        ) from exc
