# MCP Tools and Pivot Patterns

Reference for the ExtraHop MCP tools used in triage and investigation. Tool
names are shown unqualified (`extrahop_search_detections`). If your client
namespaces MCP tools by server, prefix with the server name
(`ServerName:extrahop_search_detections`).

## Contents

- Detection tools
- Device tools
- Record and packet tools
- Action tools (state-changing)
- Pivot patterns

## Detection tools

| Tool | Use |
|------|-----|
| `extrahop_search_detections` | Find detections by category, status, assignee, type, time. Returns compact summaries. |
| `extrahop_get_detection` | Full detail for one detection: risk score, participants, properties. |
| `extrahop_get_detectiontypemetadata` | Meaning of a detection `type`, its MITRE ATT&CK techniques and property definitions. |
| `extrahop_search_detectionactivity` | Correlated activity timeline for one detection. |

Time fields on `extrahop_search_detections` are epoch-millisecond integers.
Relative strings like `-1h` are **not** supported here; use negative ms (for
example `from=-86400000`) and `until=0` for now.

`extrahop_search_detections` filters **only** on `categories`, `types`,
`status`, `assignee`, `resolution`, and time. It has **no sort parameter and no
risk-score / criticality / participant / disposition filter**, and `limit` caps
at 5000. Consequences:

- Bound the pull with the server-side filters above, then paginate.
- Rank and prioritize the returned population **client-side** (risk score,
  `is_critical` participants, correlation, recency).
- The accuracy-review and disposition-coverage passes filter on `ai_disposition`
  **client-side** over a time-scoped pull — there is no server-side way to ask
  for "detections with an AI disposition."

### Enrichment cost ladder

Climb only as far as the verdict needs (cheapest first):

1. `extrahop_search_detections` summary (one bulk call; already in hand).
2. Scoped `extrahop_search_detections` for prior-disposition history (cheap).
3. `extrahop_get_detectiontypemetadata` — **cache once per detection type.**
4. `extrahop_get_detection` / `extrahop_search_detectionactivity` — per
   detection; spend on outliers and escalation candidates.
5. `extrahop_get_device` — per participant.
6. `extrahop_search_records` — expensive, ≤7d; **L2 only.**
7. `extrahop_download_pcap` — most expensive; **L2 only.**

### Tuning rules are out-of-band

There is **no `extrahop_*` tool to create, list, or manage tuning/suppression
rules.** The agent can *recommend* a tuning rule (type + participant scope +
rationale + supporting closed-detection IDs) for an operator to create in the
RevealX UI, but must never claim to have created or applied one.

## Device tools

| Tool | Use |
|------|-----|
| `extrahop_get_device` | Full device metadata by OID. Returns role, `is_critical`, OS, and `discovery_id`. Prefer this for a known OID. |
| `extrahop_search_devices` | Find devices by vendor, name (`~` for partial), role, IP/CIDR, tag, criticality, etc. |
| `extrahop_search_devicegroups` / `extrahop_list_devices_in_devicegroup` | Resolve and enumerate device groups. |
| `extrahop_search_devicetags` / `extrahop_list_devicetags_for_device` | Inspect tags. |
| `extrahop_get_appliance_metadata` | Console FQDN for deep-links: FQDN from `display_host`/`external_hostname`. |

## Record and packet tools

| Tool | Use |
|------|-----|
| `extrahop_search_records` | Query transaction records (HTTP, DNS, SSL, flow, etc.). Max 7-day window. |
| `extrahop_download_pcap` | Download packets for deep confirmation. |

`extrahop_search_records` time accepts relative strings (`-24h`, `-7d`) or
epoch ms. Filter on a specific record type or two via `types` (for example
`["~http"]`). To learn a type's fields, query it with `limit: 1` and inspect
the returned record.

Unlike `search_detections`, `search_records` is richly filterable and supports
`sort`, `limit`, and `offset` — use them to make investigation queries narrow
and ordered rather than broad dumps:

- **Compound filters** (`and`/`or`/`not` with a `rules` array) combine a
  participant with the suspicious attribute (e.g. participant `and`
  `statusCode >= 400`). Numeric operands are still strings (`"400"`).
- **Special fields** `.ipaddr` (all IP fields — use for an IP-only participant),
  `.port`, and `.any` (full-text).
- **Device pivots** use `discovery_id` across `client`/`server` (client-server
  types) or `sender`/`receiver` (e.g. `~flow`) — there is no device-OID field on
  records. Paginate with the absolute `from`/`until` from the first response.

For `extrahop_download_pcap`, use the record's `_source.first` and
`_source.last` for the packet time window (not the record timestamp), with a
small cushion, and build a BPF from the participants and ports, for example
`host 10.20.7.77 and host 10.4.0.7 and port 53`. Most expensive call; recent
windows only (packets must still be on disk).

## Metric tools

| Tool | Use |
|------|-----|
| `extrahop_search_metric_catalog` | Find valid `metric_category` / `stat_name` pairs for an `object_type` before querying. |
| `extrahop_execute_metric_query` | Query metrics (e.g. `bytes`, connection counts) — cheap corroboration of volumetric hypotheses (exfil, beaconing, scan fan-out) before pulling raw records. |

Call `search_metric_catalog` first to discover the right category/stat, then
`execute_metric_query`.

**Note: `search_detections` has no participant filter.** To find detections for
a device or IP, pull by `categories`/`types`/`status`/time and match the
participant **client-side** against each detection's participants.

## Action tools (state-changing)

These modify RevealX. Confirm with the user before calling (see SKILL.md).

| Tool | Use |
|------|-----|
| `extrahop_update_detection` | Close/triage a detection. Carries three independent fields: `status`, `ai_disposition`, and `resolution`. |
| `extrahop_create_investigation` | Open an investigation grouping detection IDs. Supports `name`, `event_ids`, `notes`, `assignee`, `status`, `assessment`. |

`extrahop_update_detection` fields:

- **`status`** — workflow state; `closed` clears the detection.
- **`ai_disposition`** — the **AI verdict**, recorded for accuracy measurement:
  `false_positive`, `benign_true_positive`, `malicious_true_positive`, or
  `indeterminate`. It is non-destructive (settable independently of `status`, so
  a Low-confidence detection can be classified `indeterminate` while left open)
  and should be set on **every** detection you reach a verdict on — it is the
  signal the SOC scores against human ground truth (the `resolution` here and
  the investigation `assessment`). Never overwrite a human-set disposition.
- **`resolution`** — whether a response occurred. Valid only when
  `status="closed"`: `action_taken` or `no_action_taken`. Reflects response,
  not verdict; default `no_action_taken`.

`extrahop_create_investigation` carries an **`assessment`** — the case-level
verdict (`malicious_true_positive`, `benign_true_positive`, `false_positive`,
`undecided`). It is the human/case-level analogue of the AI's `ai_disposition`
(its uncertainty value is `undecided`, not `indeterminate`); set both on a
confirmed case, and don't conflate them.

Close many detections via a homogeneous, user-approved batch executed per ID —
see the batch close decision tree in
[triage-workflow.md](triage-workflow.md).

## Pivot patterns

**Detection -> device.** A detection participant with `object_type` `device`
carries `object_id` (the device OID). Call
`extrahop_get_device(id=<object_id>)` for full metadata, including
`discovery_id`.

**Device -> records.** Use the device's `discovery_id` as the operand. OR
across `client`/`server` (client-server record types like `~http`,
`~dns_request`, `~ssl_open`) and `sender`/`receiver` (non-client-server types
like `~flow`):

```json
{
  "operator": "or",
  "rules": [
    {"field": "client", "operator": "=", "operand": "<discovery_id>"},
    {"field": "server", "operator": "=", "operand": "<discovery_id>"},
    {"field": "sender", "operator": "=", "operand": "<discovery_id>"},
    {"field": "receiver", "operator": "=", "operand": "<discovery_id>"}
  ]
}
```

**IP participant -> records.** Filter on `.ipaddr` with the IP as operand.

**Records -> packets.** Pivot to `extrahop_download_pcap` using the record's
`_source.first`/`_source.last` window plus a BPF from the endpoints and ports.
