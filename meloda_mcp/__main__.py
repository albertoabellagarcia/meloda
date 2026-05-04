"""Entry point for ``uvx meloda-mcp`` and ``python -m meloda_mcp``.

Runs the MCP server over stdio. The hosted Streamable-HTTP transport lives in
``meloda_mcp.http_app`` and is started by ``meloda-mcp-http`` (added in 0.4.0).
"""
from __future__ import annotations

import argparse

from .config import load_config
from .server import build_server


def main() -> None:
    parser = argparse.ArgumentParser(prog="meloda-mcp", description="Meloda MCP server (stdio).")
    parser.add_argument("--config", help="Path to YAML config (overrides MELODA_MCP_CONFIG).")
    args = parser.parse_args()

    config = load_config(args.config)
    server = build_server(config)
    server.run()


if __name__ == "__main__":
    main()
