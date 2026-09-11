from mcp.server.fastmcp import FastMCP
from mars.config.settings import get_settings
from mars.memory.store import SQLiteMemoryStore
from mars.services.search import TavilySearchService

from mars.config.settings import get_settings as _get_settings

mcp = FastMCP(
    "mars-local-tools",
    host=_get_settings().mcp_host,
    port=_get_settings().mcp_port,
)

@mcp.tool()
def web_search(query: str) -> list[dict]:
    """Search the web through Tavily."""
    return TavilySearchService().search(query)

@mcp.tool()
def memory_search(query: str, limit: int = 8) -> list[dict]:
    """Retrieve relevant persistent memories."""
    return SQLiteMemoryStore().search(query, limit)

@mcp.tool()
def memory_add(session_id: str, kind: str, content_json: str) -> int:
    """Store a JSON memory record."""
    import json
    return SQLiteMemoryStore().add(session_id, kind, json.loads(content_json))

if __name__ == "__main__":
    import socket
    import sys

    s = _get_settings()
    # If the MCP server is already running on this port, exit quietly (exit 0)
    # instead of crashing with WinError 10048 / "address already in use".
    try:
        with socket.create_connection((s.mcp_host, s.mcp_port), timeout=1):
            print(
                f"MCP server already running at http://{s.mcp_host}:{s.mcp_port}/mcp "
                "- nothing to do."
            )
            sys.exit(0)
    except OSError:
        pass  # port free -> start normally

    mcp.run(transport="streamable-http")
