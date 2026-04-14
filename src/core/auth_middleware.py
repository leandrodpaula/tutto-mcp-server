"""Middleware ASGI para proteger o endpoint MCP com Basic Auth."""

import base64
import binascii
from typing import Awaitable, Callable

from starlette.requests import Request
from starlette.responses import JSONResponse

from src.core.database import get_database
from src.core.logging import get_logger
from src.services.auth_service import AuthService, AuthServiceError

logger = get_logger(__name__)

ASGIApp = Callable[[dict, Callable, Callable], Awaitable[None]]


class MCPAuthMiddleware:
    """Middleware ASGI que exige Basic Auth para acessar o MCP."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Basic "):
            await self._send_401(scope, receive, send)
            return

        try:
            decoded = base64.b64decode(auth_header[6:]).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError):
            await self._send_401(scope, receive, send)
            return

        if ":" not in decoded:
            await self._send_401(scope, receive, send)
            return

        client_id, client_secret = decoded.split(":", 1)
        db = get_database()
        service = AuthService(db)

        try:
            await service.authenticate(client_id=client_id, client_secret=client_secret)
        except AuthServiceError as exc:
            logger.warning(f"MCP authentication failed: {exc}")
            await self._send_401(scope, receive, send)
            return

        await self.app(scope, receive, send)

    async def _send_401(self, scope: dict, receive: Callable, send: Callable) -> None:
        response = JSONResponse(
            {"detail": "Invalid authentication credentials"},
            status_code=401,
            headers={"WWW-Authenticate": "Basic"},
        )
        await response(scope, receive, send)
