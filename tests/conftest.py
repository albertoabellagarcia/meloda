"""Shared pytest fixtures for meloda-mcp tests."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
import pytest

from meloda_mcp.api_client import ApiClient
from meloda_mcp.config import Config
from meloda_mcp.server import build_server

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    with (FIXTURES / name).open() as fh:
        return json.load(fh)


async def call_tool(server, name: str, arguments: dict[str, Any] | None = None) -> Any:
    """Call a FastMCP tool and return its parsed result.

    FastMCP returns ``(content_blocks, structured_payload)`` for scalar results
    or just ``[content_blocks]`` for dict/list results. Either way, the source
    of truth is the JSON serialised inside the first ``TextContent`` block.
    """
    response = await server.call_tool(name, arguments or {})
    blocks = response[0] if isinstance(response, tuple) else response
    if not blocks:
        return None
    text = blocks[0].text
    try:
        return json.loads(text)
    except (TypeError, json.JSONDecodeError):
        return text


@pytest.fixture
def config() -> Config:
    return Config(api_base="https://test.example/api/v1")


@pytest.fixture
async def client(config: Config) -> ApiClient:
    """An ApiClient that talks to a fresh httpx.AsyncClient.

    Tests should use ``httpx_mock`` (from pytest-httpx) to register responses
    against ``https://test.example/api/v1/...``.
    """
    transport = httpx.AsyncClient(
        base_url=config.api_base,
        headers={"User-Agent": config.user_agent, "Accept": "application/json"},
    )
    api = ApiClient(config, client=transport)
    try:
        yield api
    finally:
        await transport.aclose()


@pytest.fixture
def server(config, client):
    return build_server(config, client)
