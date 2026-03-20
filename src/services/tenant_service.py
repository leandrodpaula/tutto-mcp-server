from typing import Optional
from src.models.tenant import TenantCreate
from src.repositories.tenant_repository import TenantRepository
import secrets

class TenantServiceError(Exception):
    pass

class TenantService:
    def __init__(self, repository: TenantRepository):
        self.repository = repository

    async def create_tenant(self, tenant: TenantCreate) -> dict:
        # Check if tenant with same cpf_cnpj already exists (if provided)
        if tenant.cpf_cnpj:
            existing_doc = await self.repository.collection.find_one({"cpf_cnpj": tenant.cpf_cnpj})
            if existing_doc:
                raise TenantServiceError("Tenant with this CPF/CNPJ already exists")
        
        existing_phone = await self.repository.get_by_phone(tenant.phone)
        if existing_phone:
            raise TenantServiceError("Tenant with this phone already exists")

        # Generate token if not provided
        if not tenant.token:
            tenant.token = secrets.token_hex(16)

        created_tenant = await self.repository.create(tenant)
        return created_tenant

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
