"""Main MCP server implementation using FastMCP."""

from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Tutto MCP Server")


@mcp.tool()
def hello(name: str) -> str:
    """
    Say hello to someone.
    
    Args:
        name: The name of the person to greet
        
    Returns:
        A greeting message
    """
    return f"Hello, {name}! Welcome to Tutto MCP Server."


@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """
    Add two numbers together.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        The sum of a and b
    """
    return a + b


@mcp.resource("config://server")
def get_server_config() -> str:
    """Get server configuration information."""
    return "Tutto MCP Server v0.1.0 - Configuration"


if __name__ == "__main__":
    # Run the server
    mcp.run()
