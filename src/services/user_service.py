from typing import Optional, List
from src.models.user import UserCreate, UserUpdate
from src.repositories.user_repository import UserRepository

class UserServiceError(Exception):
    pass

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, user: UserCreate) -> dict:
        # Check if user with same phone already exists for this tenant
        existing_user = await self.repository.get_by_phone(user.phone, user.tenant_id)
        if existing_user:
            raise UserServiceError(f"User with phone {user.phone} already exists for this tenant")

        created_user = await self.repository.create(user)
        return created_user

    async def get_user(self, user_id: str) -> Optional[dict]:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserServiceError("User not found")
        return user

    async def update_user(self, user_id: str, user_update: UserUpdate) -> dict:
        updated_user = await self.repository.update(user_id, user_update)
        if not updated_user:
            raise UserServiceError("User not found or update failed")
        return updated_user

    async def find_user_by_phone(self, tenant_id: str, phone: str) -> Optional[dict]:
        user = await self.repository.get_by_phone(phone, tenant_id)
        if not user:
            raise UserServiceError("User not found")
        return user

    async def list_users_by_tenant(self, tenant_id: str) -> List[dict]:
        return await self.repository.find_by_tenant(tenant_id)
