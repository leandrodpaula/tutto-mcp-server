"""Tests for text tools."""

import pytest
from src.mcp.text_tools import register_text_tools
from fastmcp import FastMCP


def test_text_tools():
    """Test text processing tools."""
    # Note: These tests check the tool functions directly
    # In a real scenario, you would test them through the MCP interface
    
    # For now, we'll just verify the module can be imported
    from src.mcp import text_tools
    assert hasattr(text_tools, 'register_text_tools')
