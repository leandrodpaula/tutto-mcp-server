"""Ponto de entrada: FastAPI app com routers HTTP e MCP montado como sub-app."""

from fastapi import Depends, FastAPI
from fastmcp import FastMCP

from src.api.routes.auth import router as auth_router
from src.api.routes.customers import router as customers_router
from src.api.routes.events import router as events_router
from src.api.routes.health import router as health_router
from src.api.routes.messages import router as messages_router
from src.api.routes.schedules import router as schedules_router
from src.api.routes.tenants import router as tenants_router
from src.core.auth_middleware import UnifiedAuthMiddleware
from src.core.config import settings
from src.core.lifespan import shared_lifespan
from src.core.logging import get_logger, setup_logging
from src.mcp.coupon_tools import register_coupon_tools
from src.mcp.message_tools import register_message_tools
from src.mcp.plan_tools import register_plan_tools
from src.mcp.schedule_tools import register_schedule_tools
from src.mcp.security_identity_tools import register_security_identity_tools
from src.mcp.session_tools import register_session_tools
from src.mcp.subscription_tools import register_subscription_tools
from src.mcp.tenant_tools import register_tenant_tools
from src.mcp.text_tools import register_text_tools
from src.mcp.user_tools import register_user_tools
from src.mcp.whatsapp_tools import register_whatsapp_tools
from src.mcp.worker_tools import register_worker_tools

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# FastMCP sem lifespan próprio; o lifespan é gerenciado pela app FastAPI principal
mcp = FastMCP("Tutto MCP Server")

# Register tool modules
register_tenant_tools(mcp)
register_text_tools(mcp)
register_worker_tools(mcp)
register_user_tools(mcp)
register_session_tools(mcp)
register_subscription_tools(mcp)
register_coupon_tools(mcp)
register_plan_tools(mcp)
register_schedule_tools(mcp)
register_message_tools(mcp)
register_whatsapp_tools(mcp)
register_security_identity_tools(mcp)

# FastAPI app principal
app = FastAPI(
    title="Tutto MCP Server",
    description="Servidor MCP com rotas HTTP FastAPI",
    lifespan=shared_lifespan,
)

# Registra routers HTTP
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(messages_router)
app.include_router(events_router)
app.include_router(customers_router)
app.include_router(schedules_router)
app.include_router(tenants_router)

# Monta o MCP como sub-app ASGI em /mcp
app.mount("/mcp", mcp.http_app())

# Adiciona o middleware de autenticação unificado globalmente
app.add_middleware(UnifiedAuthMiddleware)


def main() -> None:
    """Roda a aplicação via uvicorn."""
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.PORT,
    )


if __name__ == "__main__":
    main()
