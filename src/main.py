"""Main MCP server implementation using FastMCP."""

from fastmcp import FastMCP
from src.mcp.tenant_tools import register_tenant_tools
from src.mcp.text_tools import register_text_tools

# Initialize FastMCP server
mcp = FastMCP("Tutto MCP Server")

# Register tool modules
register_tenant_tools(mcp)
register_text_tools(mcp)


if __name__ == "__main__":
    # Run the server
    mcp.run()
