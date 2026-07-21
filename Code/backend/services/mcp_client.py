"""
LogInsight AI — MCP Client
Connects to the MCP server on port 8001 via SSE transport
using the official MCP Python SDK.
"""

import json
import logging
from typing import Any
from contextlib import asynccontextmanager

from mcp.client.sse import sse_client
from mcp import ClientSession

logger = logging.getLogger(__name__)


class MCPClient:
    """MCP client using the official SDK with SSE transport."""

    def __init__(self, server_url: str = "http://127.0.0.1:8001"):
        self.server_url = server_url.rstrip("/")
        self._sse_url = f"{self.server_url}/sse"

    @asynccontextmanager
    async def _get_session(self):
        """Create an MCP client session via SSE transport."""
        async with sse_client(url=self._sse_url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """
        Call an MCP tool via SSE transport using the official SDK.

        Args:
            tool_name: Name of the tool to call.
            arguments: Dictionary of arguments.

        Returns:
            Tool execution result as a dictionary.

        Raises:
            Exception: If the MCP server is unreachable or returns an error.
        """
        logger.info(f"Calling MCP tool: {tool_name}")

        async with self._get_session() as session:
            result = await session.call_tool(tool_name, arguments=arguments)

            # Extract text content from the MCP result
            if result.content:
                for block in result.content:
                    if hasattr(block, "text") and block.text:
                        return json.loads(block.text)

            return {"error": "MCP tool returned no content"}

    async def health_check(self) -> bool:
        """Check if the MCP server is accessible."""
        try:
            async with self._get_session() as session:
                # If we can initialize a session, the server is healthy
                return True
        except Exception:
            return False

    async def close(self):
        """Cleanup (no persistent state to close with per-call sessions)."""
        pass
