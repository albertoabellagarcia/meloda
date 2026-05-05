"""Dataset-related MCP tools.

Tools registered:
    - search_datasets        → GET /datasets
    - get_dataset            → GET /datasets/{id}
    - get_dataset_resources  → GET /datasets/{id}/resources
    - list_portal_datasets   → GET /portals/{id}/datasets
"""
from __future__ import annotations

from typing import Any, Literal

from mcp.server.fastmcp import FastMCP

from ..api_client import ApiClient

Reusability = Literal["optimum", "good", "basic", "deficient"]
Sort = Literal["harvested_at", "date_modified", "meloda_score", "title"]


def register(server: FastMCP, client: ApiClient) -> None:
    @server.tool()
    async def search_datasets(
        q: str | None = None,
        portal_id: str | None = None,
        format: str | None = None,
        license: str | None = None,
        has_geo: bool | None = None,
        reusability: Reusability | None = None,
        theme: str | None = None,
        updated_after: str | None = None,
        meloda_min: int | None = None,
        meloda_max: int | None = None,
        sort: Sort | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """Search the catalog of ~700k datasets across all monitored Spanish portals.

        Returns a paginated envelope:
        ``{data: [...], meta: {total, page, page_size, pages}, links}``.

        - ``q``: free-text search over title, description and tags.
        - ``portal_id``: restrict to a single portal (e.g. ``barcelona``, ``datos_gob_es``).
        - ``format``: filter by distribution format (e.g. ``CSV``, ``JSON``, ``SHP``).
        - ``license``: license id or title (e.g. ``cc-by``, ``CC-BY 4.0``).
        - ``has_geo``: only datasets with detected geographic coverage.
        - ``reusability``: MELODA reusability tier.
        - ``theme``: thematic category.
        - ``updated_after``: ISO 8601 date; only datasets modified after this date.
        - ``meloda_min`` / ``meloda_max``: bounds on the MELODA score (0-49).
        - ``sort``: ordering field. Defaults to ``harvested_at``.
        - ``page`` / ``page_size``: pagination. ``page_size`` is clamped 1-100 by the API.
        """
        return await client.get(
            "/datasets",
            params={
                "q": q,
                "portal_id": portal_id,
                "format": format,
                "license": license,
                "has_geo": has_geo,
                "reusability": reusability,
                "theme": theme,
                "updated_after": updated_after,
                "meloda_min": meloda_min,
                "meloda_max": meloda_max,
                "sort": sort,
                "page": page,
                "page_size": page_size,
            },
        )

    @server.tool()
    async def get_dataset(id: str) -> dict[str, Any]:
        """Fetch the full DCAT-AP metadata of a single dataset by id.

        Returns the dataset object directly (the API's ``data`` envelope is unwrapped).
        """
        body = await client.get(f"/datasets/{id}")
        return body.get("data", body)

    @server.tool()
    async def get_dataset_resources(id: str) -> dict[str, Any]:
        """List the downloadable distributions (CSV, JSON, SHP, ...) of a dataset.

        Returns ``{data: [...], meta: {total}}``. Each item includes ``url``,
        ``format``, ``mimetype``, ``size_bytes`` (if known) and an ``http_check``
        result indicating whether the resource was reachable on last harvest.
        """
        return await client.get(f"/datasets/{id}/resources")

    @server.tool()
    async def list_portal_datasets(
        portal_id: str,
        page: int = 1,
        page_size: int = 20,
        sort: Sort | None = None,
    ) -> dict[str, Any]:
        """List datasets belonging to a single portal, paginated.

        For richer filtering use ``search_datasets`` with ``portal_id=...``.
        """
        return await client.get(
            f"/portals/{portal_id}/datasets",
            params={"page": page, "page_size": page_size, "sort": sort},
        )
