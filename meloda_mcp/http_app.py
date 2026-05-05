"""Streamable HTTP transport for the meloda-mcp server.

Wraps the FastMCP streamable-HTTP app inside a thin FastAPI parent that adds:
  - per-IP rate limiting (slowapi), with the ceiling configurable via
    ``mcp.rate_limit_per_minute`` in /opt/observatory/config.yaml.
  - a ``/health`` endpoint suitable for systemd / nginx probes.
  - a ``/`` landing endpoint that points at the docs.

Exposed routes:
  - ``GET  /``         service banner with version and MCP path.
  - ``GET  /health``   liveness probe.
  - ``ANY  /mcp``      MCP Streamable HTTP transport (POST/GET/DELETE).

Run with::

    meloda-mcp-http --config /opt/observatory/config.yaml
"""
from __future__ import annotations

import argparse
import logging
import logging.handlers
import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response

from . import __version__
from .api_client import ApiClient
from .config import Config, load_config
from .server import build_server

LOGGER = logging.getLogger("meloda_mcp.http")

# Where to redirect human visitors who land on the MCP endpoint with a browser.
# Configurable via the ``MELODA_MCP_DOCS_URL`` env var; defaults to the
# spain.meloda.org docs page that ships in this repo.
_DOCS_URL = os.environ.get("MELODA_MCP_DOCS_URL", "https://spain.meloda.org/mcp.php")


def _setup_logging(cfg: Config) -> None:
    """Configure root logging. Stdout always; ``cfg.log_file`` if set."""
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if cfg.log_file:
        handlers.append(logging.handlers.WatchedFileHandler(cfg.log_file))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        handlers=handlers,
        force=True,
    )


class BrowserRedirectMiddleware(BaseHTTPMiddleware):
    """Redirect human GETs to the human-friendly docs page.

    A browser request hitting ``/mcp`` or ``/mcp/`` lands here with
    ``Accept`` containing ``text/html`` and a method of GET. MCP clients
    use POST/DELETE or set ``Accept: text/event-stream`` for streams,
    so we can safely route only the browser case to the docs URL.
    """

    def __init__(self, app, docs_url: str) -> None:
        super().__init__(app)
        self._docs_url = docs_url

    async def dispatch(self, request: Request, call_next):
        if (
            request.method == "GET"
            and request.url.path in ("/mcp", "/mcp/")
            and "text/html" in request.headers.get("accept", "")
            and "text/event-stream" not in request.headers.get("accept", "")
        ):
            return RedirectResponse(self._docs_url, status_code=302)
        response: Response = await call_next(request)
        return response


def _rate_limit_handler(_request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Convert slowapi's ``RateLimitExceeded`` into a structured JSON 429."""
    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "code": 429,
                "message": "rate limit exceeded",
                "limit": str(exc.detail),
            }
        },
    )


def build_app(config: Config | None = None) -> FastAPI:
    """Construct the FastAPI app that serves Streamable-HTTP MCP."""
    cfg = config or load_config()
    api_client = ApiClient(cfg)

    # Default safe hosts include localhost; deployments behind a reverse proxy
    # extend this with the public domain via ``mcp.allowed_hosts`` in config.yaml.
    allowed_hosts = list(cfg.allowed_hosts) or [
        "127.0.0.1:*", "localhost:*", "[::1]:*",
    ]
    allowed_origins = list(cfg.allowed_origins) or [
        "http://127.0.0.1:*", "http://localhost:*", "http://[::1]:*",
    ]

    mcp_server = build_server(
        cfg,
        api_client,
        streamable_http_path="/",
        allowed_hosts=allowed_hosts,
        allowed_origins=allowed_origins,
    )

    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[f"{cfg.rate_limit_per_minute}/minute"],
        headers_enabled=True,
    )

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[dict]:
        async with mcp_server.session_manager.run():
            try:
                yield {}
            finally:
                await api_client.aclose()

    app = FastAPI(
        title="meloda-mcp",
        version=__version__,
        description="Streamable HTTP transport for the meloda-mcp server.",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(BrowserRedirectMiddleware, docs_url=_DOCS_URL)

    @app.get("/")
    async def root() -> dict[str, str]:
        return {
            "service": "meloda-mcp",
            "version": __version__,
            "mcp_endpoint": "/mcp",
            "documentation": "https://github.com/albertoabellagarcia/meloda",
        }

    @app.get("/health")
    async def health() -> dict[str, object]:
        return {
            "status": "ok",
            "version": __version__,
            "api_base": cfg.api_base,
            "rate_limit_per_minute": cfg.rate_limit_per_minute,
        }

    app.mount("/mcp", mcp_server.streamable_http_app())
    return app


def main() -> None:
    parser = argparse.ArgumentParser(prog="meloda-mcp-http")
    parser.add_argument("--config", help="Path to YAML config")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host")
    parser.add_argument("--port", type=int, help="Bind port (overrides config)")
    args = parser.parse_args()

    cfg = load_config(args.config)
    _setup_logging(cfg)

    import uvicorn

    uvicorn.run(
        build_app(cfg),
        host=args.host,
        port=args.port or cfg.http_port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
