import secrets
from typing import Optional

from src.models.tenant import TenantCreate, TenantUpdate
from src.repositories.tenant_repository import TenantRepository


class TenantServiceError(Exception):
    pass


class TenantService:
    def __init__(self, repository: TenantRepository):
        self.repository = repository

    async def create_tenant(self, tenant: TenantCreate) -> dict:
        if tenant.cpf_cnpj:
            existing_doc = await self.repository.get_by_cpf_cnpj(tenant.cpf_cnpj)
            if existing_doc:
                raise TenantServiceError("Tenant with this CPF/CNPJ already exists")

        existing_phone = await self.repository.get_by_phone(tenant.phone)
        if existing_phone:
            raise TenantServiceError("Tenant with this phone already exists")

        if not tenant.token:
            tenant.token = secrets.token_hex(16)

        created_tenant = await self.repository.create(tenant)
        return created_tenant

    async def update_tenant(self, tenant_id: str, update: TenantUpdate) -> dict:
        update_data = update.model_dump(exclude_unset=True)
        if not update_data:
            raise TenantServiceError("No data provided for update")

        existing = await self.repository.get_by_id(tenant_id)
        if not existing:
            raise TenantServiceError("Tenant not found")

        if update.cpf_cnpj:
            other = await self.repository.get_by_cpf_cnpj(update.cpf_cnpj)
            if other and str(other.get("id")) != tenant_id:
                raise TenantServiceError("Another tenant with this CPF/CNPJ already exists")

        updated = await self.repository.update(tenant_id, update_data)
        if updated is None:
            raise TenantServiceError("Failed to update tenant")
        return updated

    async def get_tenant(self, identifier: str, by: str = "id") -> Optional[dict]:
        if by == "id":
            tenant = await self.repository.get_by_id(identifier)
        elif by == "phone":
            tenant = await self.repository.get_by_phone(identifier)
        elif by == "token":
            tenant = await self.repository.get_by_token(identifier)
        else:
            raise TenantServiceError("Invalid 'by' parameter. Use id, phone, or token.")

        if not tenant:
            raise TenantServiceError("Tenant not found")

        return tenant
