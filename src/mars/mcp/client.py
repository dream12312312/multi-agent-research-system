import asyncio
import json
import socket
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

from mars.config.settings import PROJECT_ROOT, get_settings


class LocalMCPToolClient:
    def __init__(self):
        s = get_settings()
        self.host = s.mcp_host
        self.port = s.mcp_port
        self.url = f"http://{self.host}:{self.port}/mcp"
        self._server_proc: subprocess.Popen | None = None

    def _server_reachable(self) -> bool:
        try:
            with socket.create_connection((self.host, self.port), timeout=1):
                return True
        except OSError:
            return False

    def _ensure_server(self):
        """Auto-start the local MCP server if it is not running yet."""
        if self._server_reachable():
            return
        cmd = [sys.executable, "-m", "mars.mcp.server"]
        kwargs = {"cwd": str(PROJECT_ROOT)}
        if self.host not in ("127.0.0.1", "localhost", "0.0.0.0"):
            # Remote host (e.g. docker): we cannot start it locally.
            raise ConnectionError(f"MCP server is not reachable at {self.url}")
        self._server_proc = subprocess.Popen(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kwargs
        )
        deadline = time.time() + 15
        while time.time() < deadline:
            if self._server_reachable():
                return
            time.sleep(0.3)
        raise ConnectionError(
            f"MCP server did not start within 15s at {self.url}. "
            "Run 'python -m mars.mcp.server' manually and check its output."
        )

    async def _call(self, name: str, args: dict):
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        async with streamable_http_client(self.url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(name, args)
                return result

    def _run_async(self, coro):
        self._ensure_server()
        with ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(asyncio.run, coro).result()

    def _text(self, result):
        values = []

        for item in getattr(result, "content", []) or []:
            if hasattr(item, "text"):
                values.append(item.text)

        if not values:
            return []

        try:
            return json.loads(values[0])
        except Exception:
            return values[0]

    def web_search(self, query: str):
        result = self._run_async(
            self._call("web_search", {"query": query})
        )
        return self._text(result)

    def memory_search(self, query: str, limit: int = 8):
        result = self._run_async(
            self._call(
                "memory_search",
                {"query": query, "limit": limit},
            )
        )
        return self._text(result)

    def memory_add(self, session_id: str, kind: str, content: dict):
        result = self._run_async(
            self._call(
                "memory_add",
                {
                    "session_id": session_id,
                    "kind": kind,
                    "content_json": json.dumps(content),
                },
            )
        )
        return self._text(result)