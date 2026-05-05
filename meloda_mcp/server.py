"""MCP server factory.

Wires every tool group into a single FastMCP instance bound to a shared
``ApiClient``. Use :func:`build_server` from any transport (stdio, HTTP, in-test).
"""
from __future__ import annotations

import contextlib

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from . import __version__
from .api_client import ApiClient
from .config import Config
from .tools import datasets as datasets_tools
from .tools import portals as portals_tools
from .tools import stats as stats_tools


def build_server(
    config: Config | None = None,
    client: ApiClient | None = None,
    streamable_http_path: str = "/mcp",
    allowed_hosts: list[str] | None = None,
    allowed_origins: list[str] | None = None,
) -> FastMCP:
    """Construct (but don't run) an MCP server.

    If ``client`` is provided the caller is responsible for closing it.
    Otherwise an internal client is created and registered for cleanup at
    server shutdown via the FastMCP lifespan.

    ``streamable_http_path`` controls where the MCP endpoint sits inside the
    Starlette app returned by :meth:`FastMCP.streamable_http_app`. Defaults to
    ``/mcp``. When the parent FastAPI app mounts this sub-app under its own
    ``/mcp`` prefix, set this to ``/`` to avoid a duplicated ``/mcp/mcp`` path.
    """
    cfg = config or Config()
    api = client or ApiClient(cfg)

    transport_security = TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=allowed_hosts or [
            "127.0.0.1:*", "localhost:*", "[::1]:*",
        ],
        allowed_origins=allowed_origins or [
            "http://127.0.0.1:*", "http://localhost:*", "http://[::1]:*",
        ],
    )
    server = FastMCP(
        name="meloda",
        streamable_http_path=streamable_http_path,
        transport_security=transport_security,
    )

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
