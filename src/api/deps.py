"""Dependências do FastAPI."""

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.core.database import get_database


def get_db() -> AsyncIOMotorDatabase:
    """Retorna a instância do banco de dados MongoDB."""
    return get_database()
