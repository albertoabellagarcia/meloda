"""MCP server factory.

In 0.1.0 the server registers a single placeholder tool (``ping``) so the
package can be installed and verified end-to-end before real tools land.
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import __version__
from .config import Config


def build_server(config: Config | None = None) -> FastMCP:
    """Construct (but don't run) an MCP server bound to ``config``."""
    cfg = config or Config()
    server = FastMCP(name="meloda")

    @server.tool()
    def ping() -> dict[str, str]:
        """Health check. Returns the wrapper version and the upstream API base."""
        return {"version": __version__, "api_base": cfg.api_base}

    return server
