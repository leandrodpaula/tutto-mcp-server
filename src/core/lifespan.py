"""Shared lifespan para FastAPI e MCP."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from src.core.database import close_mongo_connection, connect_to_mongo
from src.core.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def shared_lifespan(app) -> AsyncGenerator[None, None]:
    """Gerencia o ciclo de vida compartilhado da aplicação."""
    logger.info("Lifespan starting...")
    await connect_to_mongo()
    logger.info("Lifespan started.")
    yield
    logger.info("Lifespan shutting down...")
    await close_mongo_connection()
    logger.info("Lifespan shut down.")
