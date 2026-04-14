"""Rota de autenticação unificada para serviços (Basic) e customers (Google OAuth)."""

import base64
import json
from datetime import timedelta
from typing import Literal, Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

from src.api.customer_auth import create_access_token, create_refresh_token, decode_token
from src.api.deps import get_db
from src.core.config import settings
from src.core.database import get_database
from src.core.logging import get_logger
from src.repositories.customer_repository import CustomerRepository
from src.services.auth_service import AuthService, AuthServiceError
from src.services.customer_service import CustomerService, CustomerServiceError
from src.services.google_auth_service import GoogleAuthService, GoogleAuthServiceError

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


class AuthRequest(BaseModel):
    grant_type: Literal["service", "google", "refresh_token"] = Field(
        ..., description="Tipo de autenticação: 'service', 'google' ou 'refresh_token'"
    )
    client_id: Optional[str] = Field(None, description="Client ID para serviços")
    client_secret: Optional[str] = Field(None, description="Client Secret para serviços")
    google_token: Optional[str] = Field(
        None, description="ID token JWT do Google (usado quando grant_type='google')"
    )
    refresh_token: Optional[str] = Field(
        None, description="Refresh token (usado quando grant_type='refresh_token')"
    )


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = Field(None, description="Refresh token para renew")
    refresh_expires_in: Optional[int] = Field(
        None, description="Tempo de expiração do refresh token em segundos"
    )


@router.post("", response_model=AuthResponse)
async def authenticate(
    payload: AuthRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),  # noqa: B008
) -> dict:
    """Gera token JWT para serviços (client_id/client_secret) ou customers (Google token)."""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    if payload.grant_type == "service":
        if not payload.client_id or not payload.client_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id and client_secret are required for grant_type='service'",
            )

        service_db = get_database()
        auth_service = AuthService(service_db)
        try:
            identity = await auth_service.authenticate(
                client_id=payload.client_id,
                client_secret=payload.client_secret,
            )
        except AuthServiceError as exc:
            logger.warning(f"Service authentication failed: {exc}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid client_id or client_secret",
            ) from exc

        token_data = {"sub": str(identity.get("_id") or identity.get("id")), "type": "service"}
        access_token = create_access_token(data=token_data, expires_delta=access_token_expires)
        refresh_token = create_refresh_token(data=token_data)
        refresh_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": int(access_token_expires.total_seconds()),
            "refresh_token": refresh_token,
            "refresh_expires_in": int(refresh_expires.total_seconds()),
        }

    if payload.grant_type == "google":
        if not payload.google_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="google_token is required for grant_type='google'",
            )

        google_service = GoogleAuthService()
        try:
            google_payload = await google_service.verify_id_token(payload.google_token)
        except GoogleAuthServiceError as exc:
            logger.warning(f"Google token verification failed: {exc}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
            ) from exc

        email = google_payload.get("email", "").lower()
        name = google_payload.get("name", email)
        google_id = google_payload.get("sub")

        repo = CustomerRepository(db)
        service = CustomerService(repo)
        try:
            customer = await service.authenticate_or_create_google(
                email=email,
                name=name,
                google_id=google_id,
            )
        except CustomerServiceError as exc:
            logger.warning(f"Customer authentication failed: {exc}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
            ) from exc

        token_data = {"sub": customer["id"], "type": "customer"}
        access_token = create_access_token(data=token_data, expires_delta=access_token_expires)
        refresh_token = create_refresh_token(data=token_data)
        refresh_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": int(access_token_expires.total_seconds()),
            "refresh_token": refresh_token,
            "refresh_expires_in": int(refresh_expires.total_seconds()),
        }

    if payload.grant_type == "refresh_token":
        if not payload.refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="refresh_token is required for grant_type='refresh_token'",
            )
        try:
            token_payload = decode_token(payload.refresh_token)
        except jwt.ExpiredSignatureError as exc:
            logger.warning("Refresh token expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc
        except jwt.PyJWTError as exc:
            logger.warning(f"Invalid refresh token: {exc}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        subject = token_payload.get("sub")
        token_type_claim = token_payload.get("type")
        if not subject or not token_type_claim:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            data={"sub": subject, "type": token_type_claim},
            expires_delta=access_token_expires,
        )
        new_refresh_token = create_refresh_token(data={"sub": subject, "type": token_type_claim})
        refresh_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": int(access_token_expires.total_seconds()),
            "refresh_token": new_refresh_token,
            "refresh_expires_in": int(refresh_expires.total_seconds()),
        }

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid grant_type. Use 'service', 'google' or 'refresh_token'.",
    )


@router.get("/google")
async def google_auth_redirect(
    request: Request,
    tenant_id: Optional[str] = None,
) -> RedirectResponse:
    """Redireciona o usuário para a tela de autorização do Google.

    Query params:
        tenant_id: Identificador do tenant (será preservado no state).
    """
    state_payload = {"redirect_uri": str(request.url_for("google_auth_callback"))}
    if tenant_id:
        state_payload["tenant_id"] = tenant_id
    state = base64.urlsafe_b64encode(json.dumps(state_payload).encode()).decode().rstrip("=")

    google_service = GoogleAuthService()
    auth_url = google_service.get_authorization_url(state=state)
    return RedirectResponse(url=auth_url)


@router.get("/google/callback")
async def google_auth_callback(
    code: str,
    state: str,
    db: AsyncIOMotorDatabase = Depends(get_db),  # noqa: B008
) -> dict:
    """Recebe o callback do Google OAuth, valida o token e emite JWT interno.

    Query params:
        code: Authorization code do Google.
        state: Estado codificado em base64 com tenant_id e redirect_uri.
    """
    try:
        padding = 4 - len(state) % 4
        if padding != 4:
            state += "=" * padding
        state_payload = json.loads(base64.urlsafe_b64decode(state.encode()).decode())
    except Exception as exc:
        logger.warning(f"Invalid state parameter: {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter",
        ) from exc

    tenant_id = state_payload.get("tenant_id")

    google_service = GoogleAuthService()
    try:
        tokens = await google_service.exchange_code_for_token(code)
        id_token = tokens.get("id_token")
        if not id_token:
            raise GoogleAuthServiceError("No id_token returned from Google")
        google_payload = await google_service.verify_id_token(id_token)
    except GoogleAuthServiceError as exc:
        logger.warning(f"Google OAuth callback failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    email = google_payload.get("email", "").lower()
    name = google_payload.get("name", email)
    google_id = google_payload.get("sub")

    repo = CustomerRepository(db)
    service = CustomerService(repo)
    try:
        customer = await service.authenticate_or_create_google(
            email=email,
            name=name,
            google_id=google_id,
            tenant_id=tenant_id,
        )
    except CustomerServiceError as exc:
        logger.warning(f"Customer authentication via Google callback failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": customer["id"], "type": "customer"},
        expires_delta=access_token_expires,
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds()),
        "customer": {
            "id": customer["id"],
            "email": customer.get("email"),
            "name": customer.get("name"),
            "tenant_id": customer.get("tenant_id"),
        },
    }
