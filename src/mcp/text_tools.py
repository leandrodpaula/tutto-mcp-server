"""Example text processing tools."""

from fastmcp import FastMCP


def register_text_tools(mcp: FastMCP) -> None:
    """
    Register text processing tools with the MCP server.
    
    Args:
        mcp: FastMCP server instance
    """
    
    @mcp.tool()
    def uppercase_text(text: str) -> str:
        """
        Convert text to uppercase.
        
        Args:
            text: Text to convert
            
        Returns:
            Uppercase version of the text
        """
        return text.upper()
    
    @mcp.tool()
    def count_words(text: str) -> int:
        """
        Count the number of words in text.
        
        Args:
            text: Text to count words in
            
        Returns:
            Number of words
        """
        return len(text.split())
    
    @mcp.tool()
    def reverse_text(text: str) -> str:
        """
        Reverse the given text.
        
        Args:
            text: Text to reverse
            
        Returns:
            Reversed text
        """
        return text[::-1]
