"""Main MCP server implementation using FastMCP."""

import json
import logging
import sys
from contextlib import asynccontextmanager
from starlette.requests import Request
from starlette.responses import Response
from fastmcp import FastMCP, Context
from src.mcp.tenant_tools import register_tenant_tools
from src.mcp.text_tools import register_text_tools
from src.mcp.worker_tools import register_worker_tools
from src.mcp.user_tools import register_user_tools
from src.mcp.session_tools import register_session_tools
from src.mcp.subscription_tools import register_subscription_tools
from src.mcp.coupon_tools import register_coupon_tools
from src.mcp.plan_tools import register_plan_tools
from src.mcp.schedule_tools import register_schedule_tools
from src.core.config import settings
from src.core.database import connect_to_mongo, close_mongo_connection
from src.core.logging import setup_logging, get_logger

# Initialize logging
setup_logging()




@asynccontextmanager
async def lifespan(server: FastMCP):
    logger = get_logger("lifespan")
    logger.info("Lifespan starting...")
    await connect_to_mongo()
    logger.info("Lifespan started.")
    yield
    logger.info("Lifespan shutting down...")
    await close_mongo_connection()
    logger.info("Lifespan shut down.")

# Initialize FastMCP server
mcp = FastMCP("Tutto MCP Server", lifespan=lifespan)

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



    

@mcp.custom_route("/healthz", methods=["GET"], name="healthz", include_in_schema=False)
async def healthz(request: Request) -> Response:
    """Health check endpoint for Cloud Run."""
    return Response(
        content=json.dumps({"status": "ok", "service": "tutto-mcp-server"}),
        media_type="application/json",
        status_code=200,
    )


if __name__ == "__main__":
    mcp.run(transport=settings.MCP_TRANSPORT, port=settings.PORT)
