"""Configuration loading for meloda-mcp.

Resolution order (first hit wins):
  1. Explicit path passed to ``load_config``.
  2. ``MELODA_MCP_CONFIG`` environment variable.
  3. ``/opt/observatory/config.yaml`` (production default).
  4. Built-in defaults (public API, no rate limiting).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

DEFAULT_API_BASE = "https://spain.meloda.org/api/v1"
DEFAULT_RATE_LIMIT_PER_MINUTE = 60
DEFAULT_RATE_LIMIT_BURST = 20
DEFAULT_HTTP_PORT = 5002
DEFAULT_LOG_FILE: str | None = None


@dataclass(frozen=True)
class Config:
    api_base: str = DEFAULT_API_BASE
    http_port: int = DEFAULT_HTTP_PORT
    rate_limit_per_minute: int = DEFAULT_RATE_LIMIT_PER_MINUTE
    rate_limit_burst: int = DEFAULT_RATE_LIMIT_BURST
    log_file: str | None = DEFAULT_LOG_FILE
    request_timeout_s: float = 30.0
    user_agent: str = "meloda-mcp/0.1.0"
    # Hosts/Origins allowed by the MCP transport DNS-rebinding protection.
    # Defaults to localhost only; override in deployment to add the public
    # domain (e.g. ``["spain.meloda.org"]``).
    allowed_hosts: tuple[str, ...] = field(default_factory=tuple)
    allowed_origins: tuple[str, ...] = field(default_factory=tuple)
    extras: dict = field(default_factory=dict)


def _candidate_paths(explicit: str | os.PathLike[str] | None) -> list[Path]:
    paths: list[Path] = []
    if explicit:
        paths.append(Path(explicit))
    env = os.environ.get("MELODA_MCP_CONFIG")
    if env:
        paths.append(Path(env))
    paths.append(Path("/opt/observatory/config.yaml"))
    return paths


def load_config(path: str | os.PathLike[str] | None = None) -> Config:
    """Load configuration from YAML, falling back to defaults."""
    for candidate in _candidate_paths(path):
        if candidate.is_file():
            with candidate.open("r", encoding="utf-8") as fh:
                raw = yaml.safe_load(fh) or {}
            mcp_block = (raw.get("mcp") or {}) if isinstance(raw, dict) else {}
            consumed = {
                "api_base", "port", "rate_limit_per_minute",
                "rate_limit_burst", "log_file", "request_timeout_s", "user_agent",
                "allowed_hosts", "allowed_origins",
            }
            return Config(
                api_base=mcp_block.get("api_base", DEFAULT_API_BASE),
                http_port=int(mcp_block.get("port", DEFAULT_HTTP_PORT)),
                rate_limit_per_minute=int(
                    mcp_block.get("rate_limit_per_minute", DEFAULT_RATE_LIMIT_PER_MINUTE)
                ),
                rate_limit_burst=int(
                    mcp_block.get("rate_limit_burst", DEFAULT_RATE_LIMIT_BURST)
                ),
                log_file=mcp_block.get("log_file", DEFAULT_LOG_FILE),
                request_timeout_s=float(mcp_block.get("request_timeout_s", 30.0)),
                user_agent=mcp_block.get("user_agent", "meloda-mcp/0.1.0"),
                allowed_hosts=tuple(mcp_block.get("allowed_hosts") or ()),
                allowed_origins=tuple(mcp_block.get("allowed_origins") or ()),
                extras={k: v for k, v in mcp_block.items() if k not in consumed},
            )
    return Config()
