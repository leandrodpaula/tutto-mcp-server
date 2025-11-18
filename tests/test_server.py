"""Tests for MCP server tools."""

import pytest


def test_server_initialization():
    """Test that the server initializes correctly."""
    from tutto_mcp_server.server import mcp
    
    # Check that mcp instance exists
    assert mcp is not None
    assert mcp.name == "Tutto MCP Server"


def test_server_module_imports():
    """Test that all server modules can be imported."""
    # These imports should not raise any exceptions
    from tutto_mcp_server import server
    from tutto_mcp_server import __version__
    
    assert hasattr(server, 'mcp')
    assert __version__ == "0.1.0"


def test_tools_module_imports():
    """Test that tools module can be imported."""
    from tutto_mcp_server.tools import text_tools
    
    assert hasattr(text_tools, 'register_text_tools')
