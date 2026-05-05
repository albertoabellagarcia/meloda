"""Thin async HTTP client around the public REST API at /api/v1.

The MCP wrapper does not duplicate query logic; every tool maps to one or two
GET calls against the public API. This client is the single point that knows
how to talk HTTP — keeping retries, timeouts and error mapping in one place.
"""
from __future__ import annotations

from typing import Any

import httpx

from .config import Config


class ApiError(RuntimeError):
    """Raised when the upstream API returns an error or is unreachable."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def _extract_error_message(response: httpx.Response) -> str:
    """Pull the human-readable error message out of the API's error envelope."""
    try:
        body = response.json()
    except Exception:
        return response.text[:200] or response.reason_phrase
    if isinstance(body, dict):
        err = body.get("error")
        if isinstance(err, dict) and "message" in err:
            return str(err["message"])
        if isinstance(err, str):
            return err
    return response.text[:200] or response.reason_phrase


class ApiClient:
    """Async client for the Meloda REST API."""

    def __init__(self, config: Config, client: httpx.AsyncClient | None = None) -> None:
        self._config = config
        self._client = client or httpx.AsyncClient(
            base_url=config.api_base,
            timeout=config.request_timeout_s,
            headers={"User-Agent": config.user_agent, "Accept": "application/json"},
        )
        self._owns_client = client is None

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> ApiClient:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """GET ``path`` (relative to api_base) and return parsed JSON.

        Raises ``ApiError`` on transport failures, non-2xx responses, or
        non-JSON payloads.
        """
        clean = {k: v for k, v in (params or {}).items() if v is not None}
        try:
            response = await self._client.get(path, params=clean)
        except httpx.HTTPError as exc:
            raise ApiError(f"upstream API unreachable: {exc}") from exc
        if response.status_code >= 400:
            raise ApiError(
                _extract_error_message(response),
                status_code=response.status_code,
            )
        ctype = response.headers.get("content-type", "")
        if "json" not in ctype:
            raise ApiError(f"unexpected content-type from upstream: {ctype!r}")
        return response.json()
