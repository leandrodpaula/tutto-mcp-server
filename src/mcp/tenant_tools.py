from fastmcp import FastMCP
from typing import Optional, Literal
from src.core.database import get_database
from src.core.logging import get_logger

logger = get_logger(__name__)
from src.repositories.tenant_repository import TenantRepository
from src.services.tenant_service import TenantService, TenantServiceError
from src.models.tenant import TenantCreate
from src.repositories.instruction_repository import InstructionRepository
from src.services.instruction_service import InstructionService
from src.models.instruction import InstructionCreate

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
        except Exception as e:
            logger.error(f"Error creating tenant {name}: {str(e)}")
            raise
            
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
        except Exception as e:
            logger.error(f"Error retrieving tenant {identifier} by {by}: {str(e)}")
            raise

    @mcp.tool()
    async def get_tenant_instructions(tenant_id: str, type: Optional[str] = None) -> str:
        """
        Searches for available instructions (general, services, or products) for a specific tenant.

        Args:
            tenant_id: The ID of the tenant to search instructions for.
            query: An optional search term to filter by name.
        
        Returns:
            A formatted string with the list of matching instructions.
        """
        try:
            db = get_database()
            repo = InstructionRepository(db)
            service_layer = InstructionService(repo)
            
            if type:
                results = await service_layer.search_instructions(tenant_id, {'type': type,'is_active': True})
            else:
                results = await service_layer.search_instructions(tenant_id, {'is_active': True})
            
            if not results:
                return f"No instructions found for tenant {tenant_id}" + (f" matching '{type}'" if type else "")

            return results
        except Exception as e:
            logger.error(f"Error searching instructions for tenant {tenant_id}: {str(e)}")
            raise


    

    @mcp.tool()
    async def add_tenant_instruction(
        tenant_id: str, 
        name: str, 
        type: Literal["general", "service", "product"],
        text: Optional[str] = None,
        price: Optional[float] = None, 
        duration_minutes: Optional[int] = None, 
        description: Optional[str] = None, 
        instructions: Optional[str] = None
    ) -> str:
        """
        Adds a new instruction (general, service, or product) to a tenant.

        Args:
            tenant_id: The ID of the tenant.
            name: The name of the instruction.
            type: The type of instruction ('general', 'service', 'product').
            text: General text info (for 'general').
            price: The price (for 'service' or 'product').
            duration_minutes: Duration in minutes (for 'service').
            description: Description (for 'product').
            instructions: Specific instructions (for 'service').
        """
        try:
            db = get_database()
            repo = InstructionRepository(db)
            service_layer = InstructionService(repo)
            
            instruction_in = InstructionCreate(
                tenant_id=tenant_id,
                name=name,
                type=type,
                text=text,
                price=price,
                duration_minutes=duration_minutes,
                description=description,
                instructions=instructions
            )
            instruction_out = await service_layer.add_instruction(instruction_in)
            return instruction_out
        except Exception as e:
            logger.error(f"Error adding instruction '{name}' for tenant {tenant_id}: {str(e)}")
            raise


    @mcp.tool()
    async def remove_tenant_instruction(tenant_id: str, instruction_id: str) -> str:
        """
        Removes an instruction from a tenant.

        Args:
            tenant_id: The ID of the tenant.
            instruction_id: The ID of the instruction to remove.
        
        Returns:
            A string with the removed instruction details or an error message.
        """
        try:
            db = get_database()
            repo = InstructionRepository(db)
            service_layer = InstructionService(repo)
            
            instruction_out = await service_layer.remove_instruction(instruction_id)
            return f"Instruction removed successfully: {instruction_out['name']} (ID: {instruction_out['id']})"
        except Exception as e:
            logger.error(f"Error removing instruction {instruction_id} for tenant {tenant_id}: {str(e)}")
            raise

    @mcp.tool()
    async def update_tenant_instruction(
        tenant_id: str, 
        instruction_id: str, 
        name: str, 
        type: Literal["general", "service", "product"],
        text: Optional[str] = None,
        price: Optional[float] = None, 
        duration_minutes: Optional[int] = None, 
        description: Optional[str] = None, 
        instructions: Optional[str] = None
    ) -> str:
        """
        Updates an instruction of a tenant.

        Args:
            tenant_id: The ID of the tenant.
            instruction_id: The ID of the instruction to update.
            name: The name of the instruction.
            type: The type of instruction ('general', 'service', 'product').
            text: General text info (for 'general').
            price: The price (for 'service' or 'product').
            duration_minutes: Duration in minutes (for 'service').
            description: Description (for 'product').
            instructions: Specific instructions (for 'service').
        
        Returns:
            A string with the updated instruction details or an error message.
        """
        try:
            db = get_database()
            repo = InstructionRepository(db)
            service_layer = InstructionService(repo)
            
            instruction_in = InstructionCreate(
                tenant_id=tenant_id,
                name=name,
                type=type,
                text=text,
                price=price,
                duration_minutes=duration_minutes,
                description=description,
                instructions=instructions
            )
            instruction_out = await service_layer.update_instruction(instruction_id, instruction_in)
            return f"Instruction updated successfully: {instruction_out['name']} (ID: {instruction_out['id']})"
        except Exception as e:
            return f"Error updating service: {str(e)}"