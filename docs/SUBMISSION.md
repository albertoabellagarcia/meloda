# Submission copy for the Claude Connectors directory

Use the text below as the starting point when submitting to the
[Claude Connectors directory](https://www.claude.com/connectors). Trim or
expand depending on the form fields Anthropic asks for at submission time.

---

## Name

**Meloda — Spanish Open Data Monitor**

## One-line description (≤ 120 chars)

> Browse 700 000 datasets across 43 Spanish open-data portals, with MELODA reusability scores, via Model Context Protocol.

## Long description

The Spanish Open Data Reuse Monitor (`spain.meloda.org`) tracks the public
catalogs of every regional and many local Spanish administrations. This
connector exposes that catalog to Claude:

- **Search 700 000+ datasets** by keyword, portal, format, license,
  geographic coverage and MELODA reusability score.
- **Inspect any of the 43 monitored portals** — last harvest time, dataset
  count, MELODA D1–D6 breakdown.
- **Read the full DCAT-AP 2.1 catalog** as a single MCP resource.
- **Open-data friendly**: data is licensed under CC BY 4.0, the connector
  itself under Apache 2.0; no authentication, public rate limit (60
  requests per minute per IP).

Typical questions you can ask Claude:

- *"Lista los portales catalanes con MELODA medio mayor a 20."*
- *"Datasets en formato CSV con licencia CC-BY publicados en 2026."*
- *"Recursos GeoJSON sobre transporte en la Comunidad de Madrid."*
- *"Compara la cobertura de datasets entre Barcelona y Valencia."*

## Endpoint URL

```
https://spain.meloda.org/mcp
```

Transport: Streamable HTTP (MCP spec 2025-06-18).

## Authentication

None. Public, anonymous access.

## Rate limits

60 requests per minute per IP. Requests beyond the limit return HTTP 429
with a structured JSON-RPC error.

## Tools (8)

| Tool | Purpose |
|---|---|
| `search_datasets` | Full-text search with filters by portal / format / license / region / MELODA score |
| `get_dataset` | Full DCAT-AP metadata of a single dataset |
| `get_dataset_resources` | Downloadable distributions of a dataset |
| `list_portals` | List monitored portals; client-side filter by region / technology |
| `get_portal` | Portal details + MELODA breakdown |
| `list_portal_datasets` | Datasets within a single portal |
| `get_global_stats` | Catalog-wide KPIs and MELODA distribution |
| `ping` | Health check |

## Resources (5)

| URI | Content |
|---|---|
| `observatory://portals` | List of all monitored portals |
| `observatory://portal/{portal_id}` | One portal (template) |
| `observatory://dataset/{dataset_id}` | One dataset (template) |
| `observatory://dataset/{dataset_id}/resources` | Distributions of a dataset (template) |
| `observatory://catalog/dcat-ap` | Full DCAT-AP 2.1 catalog dump |

## Source code

<https://github.com/albertoabellagarcia/meloda> — Apache 2.0.

## Maintainer

Alberto Abella · `alberto.abella@transparentia.net` · <https://meloda.org>

## Privacy

The connector is a stateless wrapper over the public REST API. No user
data is stored. Access logs (timestamp, anonymised IP, tool name, response
time) are kept for at most 30 days for operational diagnostics.

## Logo

Use the favicon at <https://spain.meloda.org/favicon.ico> or request a
high-resolution version from the maintainer.
