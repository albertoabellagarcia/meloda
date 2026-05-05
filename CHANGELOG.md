# Changelog

All notable changes to **meloda-mcp** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] — 2026-05-05

### Added
- Five MCP resources backed by the public REST API:
  - `observatory://portals` — list of all monitored portals
  - `observatory://catalog/dcat-ap` — full DCAT-AP 2.1 catalog dump (JSON-LD)
  - `observatory://portal/{portal_id}` — one portal (template)
  - `observatory://dataset/{dataset_id}` — one dataset (template)
  - `observatory://dataset/{dataset_id}/resources` — distributions of a dataset (template)

## [0.3.0] — 2026-05-05

### Added
- Streamable HTTP transport. The same package now ships both a stdio entry
  point (`meloda-mcp`) and an HTTP entry point (`meloda-mcp-http`) that can be
  exposed publicly behind a reverse proxy.
- Per-IP rate limiting via `slowapi`, configurable through
  `mcp.rate_limit_per_minute` in the config YAML.
- Configurable `allowed_hosts` / `allowed_origins` for the MCP transport's
  built-in DNS-rebinding protection.
- 302 redirect from `GET /mcp` (browser) to a configurable docs URL so
  humans landing on the protocol endpoint reach a friendly page.
- `/health` and `/` endpoints on the daemon for liveness probes.

## [0.2.0] — 2026-05-04

### Added
- Seven tools wired to `https://spain.meloda.org/api/v1`:
  `search_datasets`, `get_dataset`, `get_dataset_resources`,
  `list_portals`, `get_portal`, `list_portal_datasets`, `get_global_stats`.
- API client error handling: extracts the upstream's `error.message`
  field for clearer client-side diagnostics.

## [0.1.0] — 2026-05-04

### Added
- Repository scaffold: `pyproject.toml` (hatchling + Apache-2.0),
  package layout, smoke tests, GitHub Actions CI (tests on push/PR,
  publish on tag).
- A placeholder `ping` tool to verify end-to-end install before real
  tools landed.
