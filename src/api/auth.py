"""Dependências e utilitários de autenticação unificados para a API HTTP."""

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer

from src.core.config import settings
from src.core.database import get_database
from src.core.logging import get_logger
from src.repositories.customer_repository import CustomerRepository

logger = get_logger(__name__)

# OAuth2PasswordBearer espera o token no header 'Authorization: Bearer <token>'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "token_type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "token_type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


async def _authenticate_token(token: str) -> dict:
    """Valida um token JWT e retorna a identidade (customer ou payload de service)."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    subject: Optional[str] = payload.get("sub")
    token_type: Optional[str] = payload.get("type")
    if not subject or not token_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if token_type == "customer":
        db = get_database()
        repo = CustomerRepository(db)
        customer = await repo.get_by_id(subject)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Customer not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return customer

    # token_type == "service" (ou outro tipo de serviço)
    return payload


async def require_auth(
    request: Request,
) -> dict:
    """Dependency que retorna a identidade autenticada pelo middleware global.

    Raises:
        HTTPException: 401 se a identidade não estiver no estado da requisição.
    """
    user = getattr(request.state, "user", None)
    if user:
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def require_customer_auth(
    identity: dict = Depends(require_auth),  # noqa: B008
) -> dict:
    """Wrapper que garante que a identidade autenticada é um customer."""
    # Para customers, o repo retorna o documento (sem campo 'type').
    # Para services, o payload contém 'type': 'service'.
    if isinstance(identity, dict) and identity.get("type") == "service":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer access required",
        )
    return identity
