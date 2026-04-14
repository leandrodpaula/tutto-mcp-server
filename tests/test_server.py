"""Tests for MCP server and FastAPI app."""


def test_mcp_initialization():
    """Test that the MCP server initializes correctly."""
    from src.mcp_server import mcp

    assert mcp is not None
    assert mcp.name == "Tutto MCP Server"


def test_fastapi_app_imports():
    """Test that the FastAPI app and modules can be imported."""
    from src import main as server

    assert hasattr(server, "app")
    assert hasattr(server, "main")


def test_tools_module_imports():
    """Test that tools module can be imported."""
    from src.mcp import text_tools

    assert hasattr(text_tools, "register_text_tools")
