from typing import List
from src.models.session import SessionCreate
from src.repositories.session_repository import SessionRepository

class SessionService:
    def __init__(self, repository: SessionRepository):
        self.repository = repository

    async def add_session_data(self, session: SessionCreate) -> dict:
        return await self.repository.create(session)

    async def get_session_history(self, user_id: str, tenant_id: str) -> List[dict]:
        return await self.repository.get_by_user(user_id, tenant_id)
