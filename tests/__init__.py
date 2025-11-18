"""Tests for the main MCP server."""

import pytest
from tutto_mcp_server import __version__


def test_version():
    """Test that version is defined."""
    assert __version__ == "0.1.0"
