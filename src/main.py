"""Ponto de entrada: FastAPI app com routers HTTP e MCP montado como sub-app."""

from fastapi import FastAPI

from src.api.routes.events import router as events_router
from src.api.routes.health import router as health_router
from src.api.routes.messages import router as messages_router
from src.core.config import settings
from src.core.lifespan import shared_lifespan
from src.core.logging import get_logger, setup_logging
from src.mcp_server import mcp

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# FastAPI app principal
app = FastAPI(
    title="Tutto MCP Server",
    description="Servidor MCP com rotas HTTP FastAPI",
    lifespan=shared_lifespan,
)

# Registra routers HTTP
app.include_router(health_router)
app.include_router(messages_router)
app.include_router(events_router)

# Monta o MCP como sub-app ASGI em /mcp
app.mount("/mcp", mcp.http_app())


def main() -> None:
    """Roda a aplicação via uvicorn."""
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.PORT,
    )


if __name__ == "__main__":
    main()
