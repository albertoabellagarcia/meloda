"""Tests for the Streamable HTTP transport (meloda_mcp.http_app)."""
from __future__ import annotations

import importlib.util

import pytest

from meloda_mcp.config import Config

_HTTP_AVAILABLE = importlib.util.find_spec("fastapi") is not None
pytestmark = pytest.mark.skipif(
    not _HTTP_AVAILABLE,
    reason="HTTP extras not installed (install with `.[http]`).",
)


def _build_test_app(rate_limit: int = 60):
    from fastapi.testclient import TestClient

    from meloda_mcp.http_app import build_app

    cfg = Config(
        api_base="https://test.example/api/v1",
        rate_limit_per_minute=rate_limit,
    )
    app = build_app(cfg)
    return TestClient(app)


def test_root_returns_service_banner() -> None:
    with _build_test_app() as client:
        response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "meloda-mcp"
    assert body["mcp_endpoint"] == "/mcp"


def test_health_returns_status_and_config() -> None:
    with _build_test_app(rate_limit=42) as client:
        response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["api_base"] == "https://test.example/api/v1"
    assert body["rate_limit_per_minute"] == 42


def test_mcp_endpoint_is_mounted() -> None:
    """A bare GET on /mcp should be handled by the MCP transport, not 404.

    The exact response code depends on the transport (typically 405 or 406
    for a GET without the right headers), but the route must exist.
    """
    with _build_test_app() as client:
        response = client.get("/mcp")
    assert response.status_code != 404


def test_rate_limit_returns_429_after_threshold() -> None:
    """Set rate_limit=2/minute and verify the third call is rejected."""
    with _build_test_app(rate_limit=2) as client:
        ok1 = client.get("/health")
        ok2 = client.get("/health")
        blocked = client.get("/health")
    assert ok1.status_code == 200
    assert ok2.status_code == 200
    assert blocked.status_code == 429
    err = blocked.json()
    assert err["error"]["code"] == 429
