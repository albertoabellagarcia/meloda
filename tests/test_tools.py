"""Tests for MCP tool implementations.

Each test exercises a real fixture captured from spain.meloda.org/api/v1
and asserts the tool returns the expected shape.
"""
from __future__ import annotations

from tests.conftest import call_tool, load_fixture


async def test_search_datasets_passes_through_filters(server, httpx_mock) -> None:
    fixture = load_fixture("datasets_montilla_p2.json")
    httpx_mock.add_response(
        url=(
            "https://test.example/api/v1/datasets"
            "?portal_id=montilla&page=1&page_size=2"
        ),
        json=fixture,
    )
    result = await call_tool(
        server, "search_datasets",
        {"portal_id": "montilla", "page": 1, "page_size": 2},
    )
    assert "data" in result
    assert result["meta"]["total"] == 39
    assert len(result["data"]) == 2


async def test_get_dataset_unwraps_data(server, httpx_mock) -> None:
    fixture = load_fixture("dataset_detail.json")
    httpx_mock.add_response(
        url="https://test.example/api/v1/datasets/697760",
        json=fixture,
    )
    result = await call_tool(server, "get_dataset", {"id": "697760"})
    assert result["id"] == 697760
    assert result["portal_id"] == "montilla"
    assert "meloda" in result


async def test_get_dataset_resources_returns_envelope(server, httpx_mock) -> None:
    fixture = load_fixture("dataset_resources.json")
    httpx_mock.add_response(
        url="https://test.example/api/v1/datasets/697760/resources",
        json=fixture,
    )
    result = await call_tool(server, "get_dataset_resources", {"id": "697760"})
    assert "data" in result
    assert isinstance(result["data"], list)
    if result["data"]:
        first = result["data"][0]
        assert {"id", "name", "format", "url"} <= set(first.keys())


async def test_list_portals_filters_by_region(server, httpx_mock) -> None:
    fixture = load_fixture("portals.json")
    # The tool may call the API once per invocation in this test, register
    # two responses so we don't depend on internal caching behaviour.
    httpx_mock.add_response(url="https://test.example/api/v1/portals", json=fixture)
    httpx_mock.add_response(url="https://test.example/api/v1/portals", json=fixture)

    all_result = await call_tool(server, "list_portals", {})
    cat_result = await call_tool(server, "list_portals", {"region": "Cataluña"})
    assert all_result["meta"]["total"] == 43
    assert cat_result["meta"]["total"] < all_result["meta"]["total"]
    assert all(p["region"] == "Cataluña" for p in cat_result["data"])


async def test_list_portals_filters_by_technology(server, httpx_mock) -> None:
    fixture = load_fixture("portals.json")
    httpx_mock.add_response(url="https://test.example/api/v1/portals", json=fixture)
    result = await call_tool(server, "list_portals", {"technology": "ckan"})
    assert all(p["type"].lower() == "ckan" for p in result["data"])
    assert result["meta"]["total"] > 0


async def test_get_portal_unwraps_data(server, httpx_mock) -> None:
    fixture = load_fixture("portal_montilla.json")
    httpx_mock.add_response(
        url="https://test.example/api/v1/portals/montilla",
        json=fixture,
    )
    result = await call_tool(server, "get_portal", {"id": "montilla"})
    assert result["id"] == "montilla"
    assert "meloda" in result
    assert "avg_score" in result["meloda"]


async def test_list_portal_datasets_passes_pagination(server, httpx_mock) -> None:
    fixture = load_fixture("datasets_montilla_p2.json")
    httpx_mock.add_response(
        url=(
            "https://test.example/api/v1/portals/montilla/datasets"
            "?page=1&page_size=2"
        ),
        json=fixture,
    )
    result = await call_tool(
        server, "list_portal_datasets",
        {"portal_id": "montilla", "page": 1, "page_size": 2},
    )
    assert result["meta"]["total"] == 39


async def test_get_global_stats_unwraps_data(server, httpx_mock) -> None:
    httpx_mock.add_response(
        url="https://test.example/api/v1/stats",
        json={"data": {"total_datasets": 700000, "meloda_avg": 18.4}},
    )
    result = await call_tool(server, "get_global_stats", {})
    assert result["total_datasets"] == 700000


async def test_ping_returns_version(server) -> None:
    result = await call_tool(server, "ping", {})
    assert "version" in result
    assert "api_base" in result


async def test_all_tools_listed(server) -> None:
    """Sanity check: every tool we registered is discoverable via list_tools()."""
    tools = await server.list_tools()
    names = {t.name for t in tools}
    expected = {
        "ping",
        "search_datasets",
        "get_dataset",
        "get_dataset_resources",
        "list_portal_datasets",
        "list_portals",
        "get_portal",
        "get_global_stats",
    }
    assert expected <= names
