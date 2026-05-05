"""MCP server factory.

Wires every tool group into a single FastMCP instance bound to a shared
``ApiClient``. Use :func:`build_server` from any transport (stdio, HTTP, in-test).
"""
from __future__ import annotations

import contextlib

from mcp.server.fastmcp import FastMCP

from . import __version__
from .api_client import ApiClient
from .config import Config
from .tools import datasets as datasets_tools
from .tools import portals as portals_tools
from .tools import stats as stats_tools


def build_server(
    config: Config | None = None,
    client: ApiClient | None = None,
) -> FastMCP:
    """Construct (but don't run) an MCP server.

    If ``client`` is provided the caller is responsible for closing it.
    Otherwise an internal client is created and registered for cleanup at
    server shutdown via the FastMCP lifespan.
    """
    cfg = config or Config()
    api = client or ApiClient(cfg)

    server = FastMCP(name="meloda")

    @server.tool()
    def ping() -> dict[str, str]:
        """Health check. Returns the wrapper version and the upstream API base."""
        return {"version": __version__, "api_base": cfg.api_base}

    datasets_tools.register(server, api)
    portals_tools.register(server, api)
    stats_tools.register(server, api)

    if client is None:
        @contextlib.asynccontextmanager
        async def _close_client_on_shutdown(_server: FastMCP):
            try:
                yield {}
            finally:
                await api.aclose()

        with contextlib.suppress(AttributeError):
            server.lifespan = _close_client_on_shutdown  # type: ignore[attr-defined]

    return server
