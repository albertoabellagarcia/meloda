"""Portal-related MCP tools.

Tools registered:
    - list_portals  → GET /portals (with client-side filtering)
    - get_portal    → GET /portals/{id}
"""
from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from ..api_client import ApiClient


def _matches(portal: dict[str, Any], region: str | None, technology: str | None) -> bool:
    if region and (portal.get("region") or "").lower() != region.lower():
        return False
    return not (
        technology and (portal.get("type") or "").lower() != technology.lower()
    )


def register(server: FastMCP, client: ApiClient) -> None:
    @server.tool()
    async def list_portals(
        region: str | None = None,
        technology: str | None = None,
    ) -> dict[str, Any]:
        """List the Spanish open-data portals monitored by spain.meloda.org.

        Each entry includes ``id``, ``name``, ``url``, ``type`` (CKAN/Socrata/...),
        ``region``, ``last_harvest`` and ``meloda`` summary scores.

        - ``region``: filter by region label (``Cataluña``, ``Andalucía``, ...).
          Matched case-insensitively, exact equality.
        - ``technology``: filter by portal stack (``ckan``, ``socrata``,
          ``opendatasoft``, ...). Matched case-insensitively, exact equality.

        Filtering is applied client-side because the upstream ``/portals``
        endpoint accepts no query parameters.
        """
        body = await client.get("/portals")
        items = body.get("data", []) if isinstance(body, dict) else []
        if region or technology:
            items = [p for p in items if _matches(p, region, technology)]
        return {"data": items, "meta": {"total": len(items)}}

    @server.tool()
    async def get_portal(id: str) -> dict[str, Any]:
        """Fetch detail for a single portal: harvest history summary and MELODA breakdown.

        Returns the portal object directly (the API's ``data`` envelope is unwrapped).
        """
        body = await client.get(f"/portals/{id}")
        return body.get("data", body)
