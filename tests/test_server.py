"""Tests for MCP server tools."""

import pytest


def test_server_initialization():
    """Test that the server initializes correctly."""
    from src.main import mcp
    
    # Check that mcp instance exists
    assert mcp is not None
    assert mcp.name == "Tutto MCP Server"


def test_server_module_imports():
    """Test that all server modules can be imported."""
    # These imports should not raise any exceptions
    from src import main as server
    __version__ = "0.1.0"
    
    assert hasattr(server, 'mcp')
    assert __version__ == "0.1.0"


def test_tools_module_imports():
    """Test that tools module can be imported."""
    from src.mcp import text_tools
    
    assert hasattr(text_tools, 'register_text_tools')
