"""Middleware ASGI unificado para proteger API e MCP com Bearer JWT."""

from typing import Awaitable, Callable, List

from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import HTTPException

from src.api.auth import _authenticate_token
from src.core.logging import get_logger

logger = get_logger(__name__)

ASGIApp = Callable[[dict, Callable, Callable], Awaitable[None]]


class UnifiedAuthMiddleware:
    """Middleware ASGI que exige Bearer JWT para rotas protegidas."""

    def __init__(
        self,
        app: ASGIApp,
        exempt_paths: List[str] = None,
        exempt_prefixes: List[str] = None,
    ):
        self.app = app
        self.exempt_paths = exempt_paths or ["/healthz", "/openapi.json", "/docs", "/redoc"]
        self.exempt_prefixes = exempt_prefixes or ["/auth"]

    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        path = request.url.path

        # Verifica se a rota é isenta de autenticação
        if path in self.exempt_paths:
            await self.app(scope, receive, send)
            return

        for prefix in self.exempt_prefixes:
            if path.startswith(prefix):
                await self.app(scope, receive, send)
                return

        auth_header = request.headers.get("Authorization", "")

        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                # Usa a lógica centralizada de autenticação
                identity = await _authenticate_token(token)
                
                # Armazena a identidade no estado da requisição para uso posterior
                scope["user"] = identity
                if "state" not in scope:
                    scope["state"] = {}
                scope["state"]["user"] = identity
                
                await self.app(scope, receive, send)
                return
            except HTTPException as exc:
                logger.warning(f"Authentication failed for {path}: {exc.detail}")
                await self._send_error(scope, receive, send, exc)
                return
            except Exception as exc:
                logger.error(f"Authentication unexpected error for {path}: {exc}")
                await self._send_401(scope, receive, send)
                return

        await self._send_401(scope, receive, send)

    async def _send_error(
        self,
        scope: dict,
        receive: Callable,
        send: Callable,
        exc: HTTPException,
    ) -> None:
        response = JSONResponse(
            {"detail": exc.detail},
            status_code=exc.status_code,
            headers=exc.headers,
        )
        await response(scope, receive, send)

    async def _send_401(
        self,
        scope: dict,
        receive: Callable,
        send: Callable,
        auth_scheme: str = "Bearer",
    ) -> None:
        response = JSONResponse(
            {"detail": "Authentication required"},
            status_code=401,
            headers={"WWW-Authenticate": auth_scheme},
        )
        await response(scope, receive, send)
