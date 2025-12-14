from mcp.server.fastmcp import FastMCP
import inspect

print("Has prompt attribute:", hasattr(FastMCP, 'prompt'))
if hasattr(FastMCP, 'prompt'):
    print("FastMCP.prompt signature:", inspect.signature(FastMCP.prompt))
else:
    print("FastMCP does NOT have 'prompt' attribute.")
