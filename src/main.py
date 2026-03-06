"""Main MCP server implementation using FastMCP."""

import json
from starlette.requests import Request
from starlette.responses import Response
from fastmcp import FastMCP
from src.mcp.tenant_tools import register_tenant_tools
from src.mcp.text_tools import register_text_tools

# Initialize FastMCP server
mcp = FastMCP("Tutto MCP Server")

# Register tool modules
register_tenant_tools(mcp)
register_text_tools(mcp)


@mcp.custom_route("/healthz", methods=["GET"], name="healthz", include_in_schema=False)
async def healthz(request: Request) -> Response:
    """Health check endpoint for Cloud Run."""
    return Response(
        content=json.dumps({"status": "ok", "service": "tutto-mcp-server"}),
        media_type="application/json",
        status_code=200,
    )

if __name__ == "__main__":
    # Run the server
    mcp.run()
