---
name: extrahop-rest-api
description: Generate Python code (using requests) to call the ExtraHop RevealX 360 REST API for endpoints not covered by the ExtraHop MCP server. Use this skill whenever the user asks about ExtraHop functionality that the MCP tools don't expose — including alerts, triggers, dashboards, reports, activity maps, exclusion intervals, watchlists, custom devices, network localities, bundles, threat collections, ODS targets, users, API keys, audit logs, customizations, or any endpoint under /api/v1 that the user mentions by path or operation name. Also use when the user asks "how do I do X in ExtraHop" and X isn't obviously a MCP tool, when the user wants a script they can save and rerun, or when the user references the swagger spec, OpenAPI docs, or REST API Explorer. Default to this skill over guessing endpoint shapes from memory.
---

# ExtraHop REST API (RevealX 360)

This skill helps generate accurate Python code for the ExtraHop RevealX 360 REST API — the cloud-based `/api/v1` surface authenticated via OAuth2 client credentials. The endpoint catalog is split across reference files by category; load the one that matches the user's task.

## When to use this skill vs. the ExtraHop MCP server

- **MCP server first** when the task fits a tool the MCP exposes: detection search, detection details, device search, device groups, device tags, metric queries, record search, packet download, investigations. The MCP executes calls live; this skill only generates code.
- **This skill** when the user wants:
  - Endpoints not in the MCP (alerts, triggers, dashboards, reports, exclusion intervals, watchlist mutations, custom-device CRUD, network locality entries, bundles, threat collections, ODS targets, users, audit logs, customizations, etc.)
  - A saveable script (even for MCP-covered endpoints, if they specifically want code rather than a one-shot answer)
  - A workflow that chains several REST calls together

When in doubt, mention both options to the user — "I can pull this live via the MCP, or generate a script you can save." Don't silently default to one.

## Auth pattern (OAuth2 client credentials)

The RevealX 360 API uses OAuth2 client credentials, **not** the on-prem `Authorization: ExtraHop apikey=...` pattern. The included `scripts/extrahop_client.py` handles auth, token caching, and 401 retries.

User setup (mention this when handing off code):
```bash
export EXTRAHOP_HOST=<tenant>.api.cloud.extrahop.com   # no https://, no /api/v1
export EXTRAHOP_CLIENT_ID=<client-id>
export EXTRAHOP_CLIENT_SECRET=<client-secret>
```

Credentials come from the RevealX 360 admin UI under **System Settings → API Access → REST API Credentials**. The skill assumes these are already configured — don't help the user obtain or store credentials beyond pointing at this env-var pattern.

## Code generation conventions

Always:

- Use the `ExtraHopClient` from `scripts/extrahop_client.py`. Don't write raw `requests.post(...)` calls with hardcoded URLs — the client handles auth and base URL.
- Use the `paginate_offset()` or `paginate_search()` helpers when iterating over more than one page of results. The API caps single responses (typically at 100–1000 items), so anything that might exceed that needs pagination.
- Include error handling: at minimum `resp.raise_for_status()`, and for batch operations a try/except around each item so one failure doesn't abort the run.
- Pass timestamps as **milliseconds since epoch** (the ExtraHop convention), not seconds. Relative time windows use **negative milliseconds** (e.g. `-1800000` for "the last 30 minutes").
- Quote any endpoint paths as written in the reference — paths are case-sensitive.

Don't:

- Don't invent endpoints. If the reference doesn't list it, say so and offer to check the full spec.
- Don't paste full request/response schemas inline. The references show top-level fields; for nested object shapes, point the user at the swagger spec.
- Don't include the user's `client_secret` in generated code. Always read from env vars.

## Endpoint category index

Load the matching reference file (in `references/`) when the task involves these areas. Tags overlap, so endpoints occasionally appear in two files — that's intentional for cross-navigation.

| Reference | Categories | Endpoints |
|---|---|---|
| `detections.md` | Detections, Investigations, Observations | 27 |
| `devices.md` | Device, Device Group, Custom Device, Tag, Network Locality Entry, Watchlist, Analysis Priority | 70 |
| `metrics.md` | Metrics, Dashboard, Report, Activity Map, Application | 45 |
| `records.md` | Record Log, Packet Search | 6 |
| `alerts-triggers.md` | Alert, Trigger, Exclusion Interval | 49 |
| `admin.md` | User, User Group, Auth, APIKey, Bundle, Customization, Email Group, License, Open Data Stream, Threat Collection, SSL Decrypt Key, Audit Log, Running Config, and other system endpoints | 169 |

When uncertain which reference to load, search for the user's keyword across all of them. Endpoints are listed as `### METHOD /path` headers, so grep-friendly.

## Common pitfalls to mention to the user

- **Object IDs are integers**, not strings, for most resources (devices, alerts, triggers, dashboards). Detection IDs and some newer resources use strings — the reference notes which.
- **Time ranges**: most search endpoints accept `from`/`until` in epoch milliseconds, OR a single negative `from` for relative windows. Don't mix.
- **Bulk mutations** (e.g. assigning tags to devices) are usually POSTs with an array body, not multiple single-call iterations. Check the reference before looping.
- **Deprecated endpoints** are marked ⚠️ in the references — prefer the replacement when one exists (e.g. `POST /detections/search` over the deprecated `GET /detections`).
- **Rate limits**: RevealX 360 enforces per-tenant rate limits. For scripts that hit many endpoints, suggest a small `time.sleep()` between calls or use `requests`' retry adapter.

## Workflow for answering an endpoint question

1. Identify which category the user's task falls into (use the table above).
2. Load that reference file and locate the endpoint (search for the operation name, path fragment, or summary keyword).
3. Generate a Python snippet using `ExtraHopClient`. Include only the parameters the user needs — don't dump every available field.
4. If the task requires multiple endpoints (e.g. "find all devices tagged X and pull their metrics"), chain them with intermediate variables and explain the flow.
5. Note any caveats from the reference (deprecation, pagination, time format).

If the user asks about something not in the references, say so plainly and offer to inspect the full swagger spec if it's available — or suggest they upload it.
