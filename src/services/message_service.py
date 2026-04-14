from src.models.message import MessageCreate
from src.repositories.message_repository import MessageRepository


class MessageServiceError(Exception):
    pass


class MessageService:
    def __init__(self, repository: MessageRepository):
        self.repository = repository

    async def create_message(self, message: MessageCreate) -> dict:
        created_message = await self.repository.create(message, status="pending")
        return created_message
