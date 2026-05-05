"""MCP resources for the Meloda catalog.

Resources are content addressable by URI; clients with a "browse resources" UI
(some IDE integrations, MCP Inspector) can list and read them without invoking
tools. Each resource is a thin wrapper around a single GET against the public
REST API at ``/api/v1``.

Static resources:
    observatory://portals               GET /portals
    observatory://catalog/dcat-ap       GET /catalog.jsonld

Templated resources (the URI fragment in braces is filled in by the client):
    observatory://portal/{portal_id}              GET /portals/{id}
    observatory://dataset/{dataset_id}            GET /datasets/{id}
    observatory://dataset/{dataset_id}/resources  GET /datasets/{id}/resources
"""
from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from .api_client import ApiClient


def register(server: FastMCP, client: ApiClient) -> None:
    @server.resource(
        "observatory://portals",
        name="portals",
        title="Open-data portals",
        description="List of the 43 Spanish open-data portals monitored by spain.meloda.org.",
        mime_type="application/json",
    )
    async def all_portals() -> str:
        body = await client.get("/portals")
        return json.dumps(body, ensure_ascii=False, indent=2)

    @server.resource(
        "observatory://catalog/dcat-ap",
        name="dcat-ap-catalog",
        title="DCAT-AP 2.1 catalog (JSON-LD)",
        description=(
            "Full DCAT-AP 2.1 catalog of all monitored datasets, in JSON-LD. "
            "Large payload (multiple MB); some clients may cap it. "
            "Equivalent to GET /api/v1/catalog.jsonld."
        ),
        mime_type="application/ld+json",
    )
    async def dcat_ap_catalog() -> str:
        body = await client.get("/catalog.jsonld")
        return json.dumps(body, ensure_ascii=False)

    @server.resource(
        "observatory://portal/{portal_id}",
        name="portal",
        title="Portal detail",
        description="Detail for a single portal: harvest history and MELODA breakdown.",
        mime_type="application/json",
    )
    async def one_portal(portal_id: str) -> str:
        body = await client.get(f"/portals/{portal_id}")
        return json.dumps(body, ensure_ascii=False, indent=2)

    @server.resource(
        "observatory://dataset/{dataset_id}",
        name="dataset",
        title="Dataset metadata",
        description="Full DCAT-AP metadata for a single dataset.",
        mime_type="application/json",
    )
    async def one_dataset(dataset_id: str) -> str:
        body = await client.get(f"/datasets/{dataset_id}")
        return json.dumps(body, ensure_ascii=False, indent=2)

    @server.resource(
        "observatory://dataset/{dataset_id}/resources",
        name="dataset-resources",
        title="Dataset distributions",
        description="Downloadable distributions (CSV, JSON, SHP, ...) of a dataset.",
        mime_type="application/json",
    )
    async def one_dataset_resources(dataset_id: str) -> str:
        body = await client.get(f"/datasets/{dataset_id}/resources")
        return json.dumps(body, ensure_ascii=False, indent=2)
