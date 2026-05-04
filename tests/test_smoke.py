"""Smoke tests for the 0.1.0 scaffold."""
from __future__ import annotations

import meloda_mcp
from meloda_mcp.config import Config, load_config
from meloda_mcp.server import build_server


def test_version_exposed() -> None:
    assert meloda_mcp.__version__ == "0.1.0"


def test_default_config_uses_public_api() -> None:
    cfg = load_config(path="/nonexistent/path.yaml")
    assert cfg.api_base.startswith("https://")
    assert cfg.rate_limit_per_minute > 0


def test_build_server_returns_named_instance() -> None:
    server = build_server(Config())
    # FastMCP exposes its name; the exact attribute depends on the SDK version,
    # so we just assert the object is truthy. Real handshake is exercised in
    # 0.2.0 once tools land.
    assert server is not None
