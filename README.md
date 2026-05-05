# meloda-mcp

MCP server for the **Spanish Open Data Reuse Monitor** ([spain.meloda.org](https://spain.meloda.org)).

Exposes the catalog of ~700 000 datasets across 43 monitored Spanish open-data portals to any [Model Context Protocol](https://modelcontextprotocol.io) client (Claude Desktop, Claude.ai, Cursor, VSCode, etc.).

> Status: **0.4.0 — MCP resources.** Seven tools and five resources (two static + three templated) available via the public hosted endpoint at `https://spain.meloda.org/mcp` and as a stdio package.

## What it gives you

- Search 700 k+ datasets by keyword, portal, format, license, geographic coverage, or MELODA reusability score.
- Fetch full DCAT-AP metadata of any dataset, including its distributions / resources.
- Inspect any of the 43 Spanish open-data portals: harvest history, MELODA D1–D6 breakdown, dataset counts.
- Read the catalog as DCAT-AP 2.1 JSON-LD.

## Two ways to use

### A. Via the hosted endpoint (zero install)

For Claude.ai or any MCP client that supports remote servers:

```
https://spain.meloda.org/mcp
```

(Public, anonymous, rate-limited per IP. No API key needed.)

### B. Via stdio with `uvx` (local install, no virtualenv setup)

```bash
# One-time: install uv (the modern Python package runner)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Then in your Claude Desktop config (claude_desktop_config.json):
{
  "mcpServers": {
    "meloda": {
      "command": "uvx",
      "args": ["meloda-mcp"]
    }
  }
}
```

`uvx` will fetch the package from PyPI on first run and cache it. No `pip install` needed.

### C. Via pip (for users who prefer explicit installs)

```bash
pip install meloda-mcp
meloda-mcp   # runs the stdio server
```

## Tools (available since 0.2.0)

| tool | purpose |
|---|---|
| `search_datasets` | full-text search with filters by portal / format / license / region / MELODA score |
| `get_dataset` | full metadata of a single dataset |
| `get_dataset_resources` | downloadable distributions of a dataset |
| `list_portals` | list portals with last-harvest stats; client-side filter by region / technology |
| `get_portal` | portal details + MELODA breakdown |
| `list_portal_datasets` | datasets within a single portal |
| `get_global_stats` | catalog-wide KPIs and MELODA distribution |
| `ping` | health check; returns wrapper version and configured API base |

## Resources (available since 0.4.0)

| URI | content |
|---|---|
| `observatory://portals` | list of all monitored portals |
| `observatory://portal/{portal_id}` | one portal |
| `observatory://dataset/{dataset_id}` | one dataset |
| `observatory://dataset/{dataset_id}/resources` | distributions of a dataset |
| `observatory://catalog/dcat-ap` | full DCAT-AP 2.1 catalog dump (large) |

## Data licensing

The wrapped catalog is licensed under **CC BY 4.0**. When redistributing or republishing query results, attribute *Monitor de Reutilización de Datos Abiertos de España* (`spain.meloda.org`).

The wrapper code in this repository is licensed under **Apache License 2.0** — see [`LICENSE`](LICENSE).

## Roadmap

- **0.1.0** — repo scaffold ✅
- **0.2.0** — stdio MVP with the 7 tools above ✅
- **0.3.0** — Streamable HTTP transport at `/mcp`, per-IP rate limiting ✅
- **0.4.0** — MCP resources (5 URIs, two static + three templated) ✅ *(this release)*
- **0.5.0** — PyPI publication, registry listings (Smithery, Claude Connectors)
- **1.0.0** — stable contract, semantic versioning guarantees

## Development

```bash
git clone https://github.com/albertoabellagarcia/meloda.git
cd meloda
uv sync --extra dev --extra http
uv run pytest
```

## Contributing

Issues and PRs welcome. Please discuss larger changes in an issue first.

## Releasing

See [`docs/PUBLISHING.md`](docs/PUBLISHING.md) for the operator-side checklist
(PyPI Trusted Publishing setup, tag-and-push flow, Smithery listing,
Claude Connectors submission).

The full version history lives in [`CHANGELOG.md`](CHANGELOG.md).
