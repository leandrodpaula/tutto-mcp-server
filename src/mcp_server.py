"""FastMCP server instance e registro de tools."""

from fastmcp import FastMCP

from src.mcp.coupon_tools import register_coupon_tools
from src.mcp.whatsapp_tools import register_whatsapp_tools
from src.mcp.message_tools import register_message_tools
from src.mcp.plan_tools import register_plan_tools
from src.mcp.schedule_tools import register_schedule_tools
from src.mcp.session_tools import register_session_tools
from src.mcp.subscription_tools import register_subscription_tools
from src.mcp.tenant_tools import register_tenant_tools
from src.mcp.text_tools import register_text_tools
from src.mcp.user_tools import register_user_tools
from src.mcp.worker_tools import register_worker_tools

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
