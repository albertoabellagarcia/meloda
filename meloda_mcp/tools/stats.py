"""Stats MCP tool.

Registers:
    - get_global_stats → GET /stats
"""
from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from ..api_client import ApiClient


def register(server: FastMCP, client: ApiClient) -> None:
    @server.tool()
    async def get_global_stats() -> dict[str, Any]:
        """Catalog-wide KPIs: total datasets, MELODA D1-D6 distribution, freshness.

        Note: this endpoint may be slower than the others because it aggregates
        over the full catalog. Clients should expect responses up to a few
        seconds.
        """
        body = await client.get("/stats")
        return body.get("data", body)
