from fastmcp import FastMCP
from typing import Optional, Literal
from src.core.database import get_database
from src.core.logging import get_logger

logger = get_logger(__name__)
from src.repositories.session_repository import SessionRepository
from src.services.session_service import SessionService
from src.models.session import SessionCreate, MessageData


def register_session_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    async def add_session_data(
        tenant_id: str,
        user_id: str,
        session_id: str,
        author: Literal["user", "agent"],
        session_type: str,
        session_content: str,
    ) -> str:
        """
        Adds session data (messages or events) to a user session history.

        Args:
            tenant_id: The ID of the tenant
            user_id: The ID of the user
            session_id: The ID of the session
            author: Who sent the data ('user' or 'agent')
            session_type: The type of data (e.g., 'text')
            session_content: The content of the data

        Returns:
            A string confirming success or error message.
        """
        try:
            db = get_database()
            repo = SessionRepository(db)
            service = SessionService(repo)

            message = MessageData(type=session_type, content=session_content)
            session_in = SessionCreate(
                tenant_id=tenant_id,
                user_id=user_id,
                session_id=session_id,
                author=author,
                message=message,
            )

            result = await service.add_session_data(session_in)
            return f"Session data added successfully: {result}"
        except Exception as e:
            logger.error(f"Error adding session data for {session_id}: {str(e)}")
            raise

    @mcp.tool()
    async def get_session_history(tenant_id: str, user_id: str) -> str:
        """
        Retrieves the history for a specific session.

        Args:
            tenant_id: The ID of the tenant
            user_id: The ID of the user

        Returns:
            A string with the list of session data or an error message.
        """
        try:
            db = get_database()
            repo = SessionRepository(db)
            service = SessionService(repo)

            history = await service.get_session_history(user_id, tenant_id)
            return f"Session history for {user_id}: {history}"
        except Exception as e:
            logger.error(
                f"Error retrieving history for user {user_id} in tenant {tenant_id}: {str(e)}"
            )
            raise
