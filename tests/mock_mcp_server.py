
import asyncio
from mcp.server.fastmcp import FastMCP

# Create a simple MCP server
mcp = FastMCP("EchoServer")

@mcp.tool()
def echo_tool(message: str) -> str:
    """Echoes the message back."""
    return f"Echo: {message}"

@mcp.tool()
def add_tool(a: int, b: int) -> int:
    """Adds two numbers."""
    return a + b

if __name__ == "__main__":
    # Run via stdio for simplicity in testing, or we can use SSE if we want to test that path.
    # Our RemoteMCPClient supports 'sse' and 'http'.
    # Let's try to run it as a script that our client connects to via stdio first (easiest),
    # BUT our RemoteMCPClient is designed for *Remote* (HTTP/SSE) URLs.
    # To test RemoteMCPClient, we need this server to listen on a port.
    
    # FastMCP run() defaults to stdio if no transport arg, or 'sse' if transport='sse'.
    # But 'sse' requires uvicorn/starlette.
    mcp.run(transport="sse") 
