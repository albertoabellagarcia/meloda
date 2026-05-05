"""Tests for the API client error handling and request shaping."""
from __future__ import annotations

import pytest

from meloda_mcp.api_client import ApiClient, ApiError


async def test_drops_none_params(client: ApiClient, httpx_mock) -> None:
    httpx_mock.add_response(
        url="https://test.example/api/v1/datasets?page=1&page_size=20",
        json={"data": [], "meta": {"total": 0}},
    )
    body = await client.get(
        "/datasets",
        params={"q": None, "page": 1, "page_size": 20, "format": None},
    )
    assert body == {"data": [], "meta": {"total": 0}}


async def test_extracts_api_error_message(client: ApiClient, httpx_mock) -> None:
    httpx_mock.add_response(
        url="https://test.example/api/v1/datasets/9999",
        status_code=404,
        json={"error": {"code": 404, "message": "Dataset 9999 no encontrado."}},
    )
    with pytest.raises(ApiError, match="Dataset 9999 no encontrado"):
        await client.get("/datasets/9999")


async def test_raises_on_non_json_response(client: ApiClient, httpx_mock) -> None:
    httpx_mock.add_response(
        url="https://test.example/api/v1/whatever",
        text="<html>oops</html>",
        headers={"content-type": "text/html"},
    )
    with pytest.raises(ApiError, match="unexpected content-type"):
        await client.get("/whatever")


async def test_wraps_transport_error(client: ApiClient, httpx_mock) -> None:
    import httpx

    httpx_mock.add_exception(httpx.ConnectError("nope"))
    with pytest.raises(ApiError, match="upstream API unreachable"):
        await client.get("/datasets")
