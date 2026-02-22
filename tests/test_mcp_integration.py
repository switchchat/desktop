
import asyncio
import os
import sys
import threading
import time
import uvicorn
import requests
from multiprocessing import Process

# Add app path to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../app/frontend/python_backend")))

from mcp_client import RemoteMCPClient

# Define the server process
def run_server():
    # Import inside process to avoid scope issues
    from mcp.server.fastmcp import FastMCP
    
    mcp = FastMCP("EchoServer")

    @mcp.tool()
    def echo_tool(message: str) -> str:
        """Echoes the message back."""
        return f"Echo: {message}"

    # Run on port 8001 (FastMCP uses uvicorn under the hood for sse, but we might need to configure it differently or it defaults to 8000)
    # The 'run' method signature for FastMCP might not accept 'port' directly if it's wrapping uvicorn.run inside.
    # Let's check documentation or source. But for now, let's try standard uvicorn run if possible.
    # Actually, FastMCP usually exposes run(transport="sse") which runs on 8000 by default.
    # Let's try to set port if possible, or just use default 8000 and hope it doesn't conflict with our main app.
    # But main app is running on 8000. Let's kill main app first if needed.
    # Or, let's try to pass kwargs to uvicorn if supported.
    
    # Based on error: TypeError: FastMCP.run() got an unexpected keyword argument 'port'
    # It seems we can't set port directly.
    # We might need to use `mcp._sse_server` and run uvicorn manually.
    
    # Workaround: Run on default port (8000) and ensure main app is stopped.
    # But wait, we can just use `uvicorn.run(mcp._sse_app, port=8001)` if we can access the app.
    # Let's try to inspect mcp object.
    
    # Better approach: Just use stdio transport for the test server and use stdio_client in the test.
    # This avoids port conflicts and HTTP complexity for a simple integration test.
    # But wait, we wanted to test RemoteMCPClient which uses HTTP/SSE.
    
    # Let's try to run uvicorn manually if we can get the app.
    # FastMCP doesn't expose the app easily in `run`.
    # However, `mcp.run` is just a helper.
    
    # Let's try to import uvicorn and run it.
    # But FastMCP constructs the Starlette app inside `run`.
    
    # Alternative: Use `mcp.server.fastmcp.FastMCP` but look at source.
    # Let's try to set environment variable PORT? No.
    
    # Let's try to use the `mcp` CLI to run the server script!
    # `uv run mcp run tests/mock_mcp_server.py --transport sse --port 8001`
    # But we don't have `uv` or `mcp` CLI easily available in this script.
    
    # Let's try to bind to a different port by patching uvicorn.run or just accept 8000.
    # I will stop the main server (if running) and use 8000.
    mcp.run(transport="sse")

async def test_integration():
    print("Starting Mock MCP Server on port 8000 (Default)...")
    # Ensure port 8000 is free
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 8000))
    if result == 0:
        print("Port 8000 is in use. Please stop the main server.")
        return
    sock.close()

    server_process = Process(target=run_server)
    server_process.start()
    
    # Wait for server to start
    time.sleep(5)
    
    try:
        print("Connecting Client to http://localhost:8000/sse ...")
        # Note: FastMCP default SSE endpoint is /sse
        client = RemoteMCPClient("LocalTest", "http://localhost:8000/sse", transport_type="sse")
        
        await client.connect()
        
        if not client.session:
            print("FAILED: Could not connect to server.")
            return

        print("Connected! Fetching tools...")
        tools = client._tools_cache
        print(f"Tools found: {[t['name'] for t in tools]}")
        
        if "echo_tool" not in [t['name'] for t in tools]:
            print("FAILED: echo_tool not found.")
        else:
            print("SUCCESS: Tools discovered.")

        print("Calling echo_tool...")
        result = await client.call_tool("echo_tool", {"message": "Hello MCP"})
        print(f"Result: {result}")
        
        if "Echo: Hello MCP" in str(result):
            print("SUCCESS: Tool execution verified.")
        else:
            print("FAILED: Unexpected result.")

        await client.close()
        
    finally:
        server_process.terminate()
        server_process.join()
        print("Test teardown complete.")

if __name__ == "__main__":
    asyncio.run(test_integration())
