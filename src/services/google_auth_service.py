"""Serviço para integração com autenticação Google OAuth 2.0."""

import httpx

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_TOKENINFO_ENDPOINT = "https://oauth2.googleapis.com/tokeninfo"
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"


class GoogleAuthServiceError(Exception):
    """Exceção customizada para erros na autenticação Google."""

    pass


class GoogleAuthService:
    """Serviço que valida tokens Google e troca authorization codes."""

    def __init__(self) -> None:
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI

    def get_authorization_url(self, state: str, scope: str = "openid email profile") -> str:
        """Monta a URL de autorização do Google OAuth 2.0.

        Args:
            state: Estado a ser preservado no callback.
            scope: Escopos solicitados.

        Returns:
            URL completa para redirecionamento.
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": scope,
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{GOOGLE_AUTH_URL}?{query}"

    async def exchange_code_for_token(self, code: str) -> dict:
        """Troca um authorization code por tokens do Google.

        Args:
            code: Authorization code recebido no callback.

        Returns:
            Dicionário com os tokens retornados pelo Google.

        Raises:
            GoogleAuthServiceError: Se a troca falhar.
        """
        if not self.client_id or not self.client_secret:
            raise GoogleAuthServiceError("Google OAuth credentials are not configured")

        payload = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(GOOGLE_TOKEN_ENDPOINT, data=payload)

        if response.status_code != 200:
            logger.error(f"Google token exchange failed: {response.text}")
            raise GoogleAuthServiceError("Failed to exchange authorization code")

        return response.json()

    async def verify_id_token(self, id_token: str) -> dict:
        """Valida um ID token JWT do Google via endpoint tokeninfo.

        Args:
            id_token: ID token recebido do Google.

        Returns:
            Payload decodificado do token com claims como email, sub, name, etc.

        Raises:
            GoogleAuthServiceError: Se o token for inválido ou expirado.
        """
        if not self.client_id:
            raise GoogleAuthServiceError("Google client_id is not configured")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                GOOGLE_TOKENINFO_ENDPOINT,
                params={"id_token": id_token},
            )

        if response.status_code != 200:
            logger.error(f"Google ID token verification failed: {response.text}")
            raise GoogleAuthServiceError("Invalid Google ID token")

        payload = response.json()

        # Valida audience
        audience = payload.get("aud")
        if audience != self.client_id:
            logger.error(f"Google ID token audience mismatch: {audience}")
            raise GoogleAuthServiceError("Invalid token audience")

        # Valida issuer
        issuer = payload.get("iss")
        if issuer not in ("https://accounts.google.com", "accounts.google.com"):
            logger.error(f"Google ID token issuer mismatch: {issuer}")
            raise GoogleAuthServiceError("Invalid token issuer")

        return payload
