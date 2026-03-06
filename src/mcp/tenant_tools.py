from fastmcp import FastMCP
from typing import Optional
from src.core.database import get_database
from src.repositories.tenant_repository import TenantRepository
from src.services.tenant_service import TenantService, TenantServiceError
from src.models.tenant import TenantCreate

def register_tenant_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    async def create_tenant(name: str, document: str, phone: str, domain: Optional[str] = None, token: Optional[str] = None) -> str:
        """
        Creates a new tenant in the system.

        Args:
            name: The name of the tenant (e.g., 'Tutto Barbershop')
            document: The business document or ID (e.g., '12.345.678/0001-90')
            phone: The contact phone number of the tenant
            domain: The custom domain for the tenant (optional)
            token: An authorization token (optional, will be generated if not provided)
        
        Returns:
            A string with the created tenant details or error message.
        """
        try:
            db = get_database()
            repo = TenantRepository(db)
            service = TenantService(repo)
            
            tenant_in = TenantCreate(name=name, document=document, phone=phone, domain=domain, token=token)
            tenant_out = await service.create_tenant(tenant_in)
            return f"Tenant created successfully: {tenant_out}"
        except TenantServiceError as e:
            return f"Error creating tenant: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
            
    @mcp.tool()
    async def get_tenant(identifier: str, by: str = "id") -> str:
        """
        Retrieves a tenant based on a given identifier.

        Args:
            identifier: The value of the identifier (e.g., tenant ID, phone, or token)
            by: The type of the identifier. Must be 'id', 'phone', or 'token'
        
        Returns:
            A string with the tenant details or a not found/error message.
        """
        try:
            db = get_database()
            repo = TenantRepository(db)
            service = TenantService(repo)
            
            tenant_out = await service.get_tenant(identifier, by)
            return f"Tenant found: {tenant_out}"
        except TenantServiceError as e:
            return f"Error retrieving tenant: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
