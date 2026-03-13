from fastmcp import FastMCP
from typing import Optional
from src.core.database import get_database
from src.repositories.user_repository import UserRepository
from src.services.user_service import UserService, UserServiceError
from src.models.user import UserCreate, UserUpdate

def register_user_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    async def create_user(tenant_id: str, phone: str, nome: str, email: Optional[str] = None) -> str:
        """
        Registers a new user for a specific tenant.

        Args:
            tenant_id: The ID of the tenant the user belongs to
            phone: The user's phone number
            nome: The user's name
            email: The user's email address (optional)
        
        Returns:
            A string with the created user details or error message.
        """
        try:
            db = get_database()
            repo = UserRepository(db)
            service = UserService(repo)
            
            user_in = UserCreate(tenant_id=tenant_id, phone=phone, nome=nome, email=email)
            user_out = await service.create_user(user_in)
            return f"User registered successfully: {user_out}"
        except UserServiceError as e:
            return f"Error registering user: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def get_user(user_id: str) -> str:
        """
        Retrieves a user's details by their ID.

        Args:
            user_id: The unique ID of the user
        
        Returns:
            A string with the user details or error message.
        """
        try:
            db = get_database()
            repo = UserRepository(db)
            service = UserService(repo)
            
            user_out = await service.get_user(user_id)
            return f"User found: {user_out}"
        except UserServiceError as e:
            return f"Error retrieving user: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def update_user(user_id: str, phone: Optional[str] = None, nome: Optional[str] = None, email: Optional[str] = None) -> str:
        """
        Updates an existing user's information.

        Args:
            user_id: The unique ID of the user to update
            phone: The new phone number (optional)
            nome: The new name (optional)
            email: The new email address (optional)
        
        Returns:
            A string with the updated user details or error message.
        """
        try:
            db = get_database()
            repo = UserRepository(db)
            service = UserService(repo)
            
            user_update = UserUpdate(phone=phone, nome=nome, email=email)
            user_out = await service.update_user(user_id, user_update)
            return f"User updated successfully: {user_out}"
        except UserServiceError as e:
            return f"Error updating user: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def find_user(tenant_id: str, phone: str) -> str:
        """
        Finds a user by phone number within a specific tenant.

        Args:
            tenant_id: The ID of the tenant
            phone: The user's phone number
        
        Returns:
            A string with the user details or error message.
        """
        try:
            db = get_database()
            repo = UserRepository(db)
            service = UserService(repo)
            
            user_out = await service.find_user_by_phone(tenant_id, phone)
            return f"User found: {user_out}"
        except UserServiceError as e:
            return f"Error finding user: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def list_users(tenant_id: str) -> str:
        """
        Lists all users associated with a specific tenant.

        Args:
            tenant_id: The identification of the tenant
        
        Returns:
            A string with the list of users or error message.
        """
        try:
            db = get_database()
            repo = UserRepository(db)
            service = UserService(repo)
            
            users = await service.list_users_by_tenant(tenant_id)
            return f"Users for tenant {tenant_id}: {users}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
