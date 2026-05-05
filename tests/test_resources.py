"""Tests for the MCP resources exposed by ``meloda_mcp.resources``."""
from __future__ import annotations

import json

from tests.conftest import load_fixture


async def test_portals_resource_listed_and_readable(server, httpx_mock) -> None:
    fixture = load_fixture("portals.json")
    httpx_mock.add_response(
        url="https://test.example/api/v1/portals",
        json=fixture,
    )
    static = await server.list_resources()
    uris = {str(r.uri) for r in static}
    assert "observatory://portals" in uris
    assert "observatory://catalog/dcat-ap" in uris

    contents = await server.read_resource("observatory://portals")
    assert contents
    body = json.loads(contents[0].content)
    assert body["meta"]["total"] == 43


async def test_resource_templates_listed(server) -> None:
    templates = await server.list_resource_templates()
    patterns = {t.uriTemplate for t in templates}
    assert "observatory://portal/{portal_id}" in patterns
    assert "observatory://dataset/{dataset_id}" in patterns
    assert "observatory://dataset/{dataset_id}/resources" in patterns


async def test_portal_resource_template_reads_one(server, httpx_mock) -> None:
    fixture = load_fixture("portal_montilla.json")
    httpx_mock.add_response(
        url="https://test.example/api/v1/portals/montilla",
        json=fixture,
    )
    contents = await server.read_resource("observatory://portal/montilla")
    body = json.loads(contents[0].content)
    assert body["data"]["id"] == "montilla"
    assert body["data"]["region"] == "Andalucía"


async def test_dataset_resource_template_reads_one(server, httpx_mock) -> None:
    fixture = load_fixture("dataset_detail.json")
    httpx_mock.add_response(
        url="https://test.example/api/v1/datasets/697760",
        json=fixture,
    )
    contents = await server.read_resource("observatory://dataset/697760")
    body = json.loads(contents[0].content)
    assert body["data"]["id"] == 697760


async def test_dataset_resources_template_reads_distributions(server, httpx_mock) -> None:
    fixture = load_fixture("dataset_resources.json")
    httpx_mock.add_response(
        url="https://test.example/api/v1/datasets/697760/resources",
        json=fixture,
    )
    contents = await server.read_resource("observatory://dataset/697760/resources")
    body = json.loads(contents[0].content)
    assert "data" in body
    assert isinstance(body["data"], list)


async def test_catalog_resource_returns_jsonld(server, httpx_mock) -> None:
    """The full catalog dump is exposed as a single resource."""
    httpx_mock.add_response(
        url="https://test.example/api/v1/catalog.jsonld",
        json={"@context": "http://www.w3.org/ns/dcat#", "@graph": []},
    )
    contents = await server.read_resource("observatory://catalog/dcat-ap")
    assert contents[0].mime_type == "application/ld+json"
    body = json.loads(contents[0].content)
    assert "@context" in body
