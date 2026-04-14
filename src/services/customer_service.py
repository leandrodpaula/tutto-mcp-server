"""Business logic for customer auth and management."""

from datetime import datetime, timezone
from typing import Optional

from src.repositories.customer_repository import CustomerRepository


class CustomerServiceError(Exception):
    """Exceção customizada para erros no domínio de Customer."""

    pass


class CustomerService:
    def __init__(self, repository: CustomerRepository):
        self.repository = repository

    async def register(self, data: dict) -> dict:
        email = data.get("email", "").lower().strip()
        phone = data.get("phone", "")
        tenant_id = data.get("tenant_id")

        if not email:
            raise CustomerServiceError("Email is required")
        if not tenant_id:
            raise CustomerServiceError("tenant_id is required")

        existing_email = await self.repository.get_by_email(email)
        if existing_email:
            raise CustomerServiceError("Customer with this email already exists")

        existing_phone = await self.repository.get_by_phone(phone)
        if existing_phone:
            raise CustomerServiceError("Customer with this phone already exists")

        customer_data = {
            "tenant_id": tenant_id,
            "name": data.get("name"),
            "email": email,
            "phone": phone,
            "google_id": data.get("google_id"),
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        return await self.repository.create(customer_data)

    async def authenticate_or_create_google(
        self,
        email: str,
        name: str,
        google_id: str,
        tenant_id: Optional[str] = None,
    ) -> dict:
        """Autentica um customer via Google OAuth; cria se não existir.

        Args:
            email: Email do Google.
            name: Nome do Google.
            google_id: Identificador único do Google (sub).
            tenant_id: Tenant ao qual vincular em caso de criação.

        Returns:
            Documento do customer.

        Raises:
            CustomerServiceError: Se não encontrar e tenant_id não for fornecido.
        """
        customer = await self.repository.get_by_google_id(google_id)
        if customer:
            return customer

        customer = await self.repository.get_by_email(email.lower().strip())
        if customer:
            # Vincula google_id se ainda não tiver
            if not customer.get("google_id"):
                await self.repository.update(customer["id"], {"google_id": google_id})
                customer["google_id"] = google_id
            return customer

        if not tenant_id:
            raise CustomerServiceError("Customer not found and tenant_id is required for signup")

        return await self.register(
            {
                "tenant_id": tenant_id,
                "name": name,
                "email": email,
                "phone": "",  # será preenchido posteriormente se necessário
                "google_id": google_id,
            }
        )

    async def get_profile(self, customer_id: str) -> dict:
        customer = await self.repository.get_by_id(customer_id)
        if not customer:
            raise CustomerServiceError("Customer not found")
        return customer
