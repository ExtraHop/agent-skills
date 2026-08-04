# Console URL Construction

Embed deep-links into the RevealX console so the user can jump from a finding to the exact protocol page and time window in one click. The chat session is the diagnosis; the console is where they take it forward.

---

## When to construct URLs

Build a URL whenever the report names a navigable target. Specifically:

- **Findings bullets** — link the device or device group identifier the first time it appears in a finding bullet. When the finding is about a specific protocol on that device (HTTP, DNS, SMB, etc.), point at the protocol page, not the overview. When the bullet is about overall device health or there's no single dominant protocol, point at the overview.
- **Drill in further** — any item that names a device or device group should link to the relevant console page (overview, or the protocol that matters).
- **What to do** — when the action is "investigate `<device>`" or "verify reachability of `<device>`," link the identifier to its overview page.
- **Key insight** — link identifiers the first time they appear if they weren't already linked above. Don't double-link the same identifier in the same report.

Skip URLs in:

- **Detailed mode YAML footer.** Identifiers there are for machine parsing.
- **Stale data refusal reports.** The console can't show data that doesn't exist; sending the user there is hostile.
- **Quick-look mode.** Intentionally minimal.
- **Tagging mode reports.** Operator-facing summary, not investigation.

---

## Prerequisites: hostname and appliance UUID

Every console URL needs the console FQDN; device URLs additionally need an appliance UUID.

- **Console FQDN** (e.g. `revealx.example.com`) — the customer's RevealX hostname. Forms the URL base: `https://<fqdn>/extrahop/#/`. Obtained from the `extrahop_get_appliance_metadata` tool (see Acquisition order below).
- **Appliance UUID** — a 32-character hex string identifying the appliance hosting the data. Required for device URLs (`<appliance_uuid>.<discovery_id>`). Not required for device-group URLs. Also obtained from `extrahop_get_appliance_metadata`.

The `extrahop_get_appliance_metadata` tool returns both pieces, but the field names are counter-intuitive — read them carefully:

| Field | Holds | Use for |
|---|---|---|
| `display_host` | The console FQDN (e.g. `revealx.example.com`) | **FQDN** — primary source |
| `external_hostname` | Usually the same FQDN | **FQDN** — fallback if `display_host` is empty |
| `hostname` | The 32-hex **appliance UUID** (NOT a hostname) | **Appliance UUID** |
| `mgmt_ipaddr` | Management IP | Never use for URLs |

So one call yields both the FQDN (`display_host`) and the appliance UUID (`hostname`). Acquire each piece **once per session**, then cache and reuse.

### Acquiring the FQDN and UUID

1. **Call `extrahop_get_appliance_metadata`.** This is the canonical source for both. Read the **FQDN** from `display_host` (fall back to `external_hostname`), and the **appliance UUID** from `hostname`. Do not be misled by the field name: `hostname` is the UUID, not the FQDN. If the response is missing `display_host`/`external_hostname`, do not substitute `hostname` or `mgmt_ipaddr` — treat the FQDN as unavailable. Call it once and cache both values for the rest of the session.

2. **(Fallback) Parse a URL the user already pasted** in this conversation, matching the pattern `https://<fqdn>/extrahop/#/...`. Use this only if `extrahop_get_appliance_metadata` is unavailable or returned no usable FQDN. A pasted device URL of the form `/metrics/devices/<32hex>.<16hex>/` yields both the FQDN and the appliance UUID (the 32-hex prefix).

3. **No FQDN → no links.** If `extrahop_get_appliance_metadata` is unavailable (the user is on an older MCP server that doesn't expose it) and no FQDN is available another way, **do not construct any links.** Emit the report with plain backticked identifiers. A correct unlinked report is strictly better than a fabricated one. Do not guess the hostname.

If you have the FQDN but not the UUID (for example, only a non-device URL was pasted and `extrahop_get_appliance_metadata` is unavailable), build the URLs that need only the FQDN (device groups) and skip device-level links rather than fabricating the UUID. Don't derail an investigation to chase the UUID.

### Caching

Cache both pieces for the rest of the session as soon as you have them. Don't re-call `extrahop_get_appliance_metadata` per finding. If the user opens a new session, you'll re-acquire — that's fine, it's one tool call.

### Never fabricate

- Never invent the FQDN. Plausible-looking domains (`acme.extrahop.com`, `customer.cloud.extrahop.com`) are a trap — a wrong host sends the operator to an unrelated tenant's data or to a 404. Worse, in shared-screen demos a wrong FQDN can leak the existence of other customers. If you have no FQDN, emit the report unlinked.
- Never use the **management IP** (`mgmt_ipaddr`) as the FQDN. Most modern deployments require the FQDN for cert validation, and an IP-based URL may not resolve to the console UI at all. Only use the IP if the user explicitly says that's their access path.
- Never confuse the `hostname` field (the appliance UUID) with the FQDN. Building `https://<32hex>/extrahop/#/...` produces a broken link.
- Never invent the appliance UUID. The 32-hex value isn't guessable and the user has no way to spot a wrong one until they click.
- If you have one piece but not the other, use what you have where it suffices (e.g. device-group URLs only need the FQDN) and skip the rest.

---

## URL syntax

### Device pages

**Overview** (general device page, with time window):

```
https://<hostname>/extrahop/#/metrics/devices/<appliance_uuid>.<discovery_id>/overview/?from=<N>&interval_type=<UNIT>&until=0
```

Overview also accepts the same time params as protocol pages. Use them — the operator should land on the page scoped to the assessment window, not the console's default interval.

**Protocol page** on a device:

```
https://<hostname>/extrahop/#/metrics/devices/<appliance_uuid>.<discovery_id>/<protocol-slug>?from=<N>&interval_type=<UNIT>&until=0
```

The composite device identifier is `<appliance_uuid>.<discovery_id>`:

- `appliance_uuid` — 32 hex chars, environment-constant (see Prerequisites).
- `discovery_id` — 16 hex chars, returned by `extrahop_get_device` as either `discovery_id` or `extrahop_id`. Both fields carry the same value; use whichever is present.

The `<protocol-slug>` is `overview`, `tcp`, `network`, or a protocol-specific slug — see the slug table below.

### Device group pages

```
https://<hostname>/extrahop/#/metrics/devicegroups/<group_id>/<protocol-slug>?from=<N>&interval_type=<UNIT>&until=0
```

`group_id` is the integer returned by `extrahop_search_devicegroups` as `id`. No appliance UUID is needed for device-group URLs.

### Time parameters

Two formats. **Relative time** (the default — assessment window ends "now") and **absolute time** (a fixed window not anchored to now).

#### Relative time

Pair `from` and `interval_type` to express a relative window ending now (`until=0`). The `from` value is a count of `interval_type` units back from now.

| Assessment window | `from` | `interval_type` |
|---|---|---|
| Last 30 minutes | `30` | `MIN` |
| Last 1 hour | `1` | `HR` |
| Last 6 hours | `6` | `HR` |
| Last 24 hours | `1` | `DAY` |
| Last 7 days | `1` | `WK` |
| Last 30 days | `30` | `DAY` |

Match the URL window to the assessment window. A report on "last 1 hour" linked to a 7-day URL is misleading — the operator opens the page and sees different data than the report described.

#### Absolute time

When the assessment is anchored to a fixed window — typically a scheduled run that just completed, an audit covering a specific business hour, or a post-incident review of "2:00 PM to 3:00 PM yesterday" — use absolute epoch-**second** timestamps (10-digit integers). Omit `interval_type`:

```
?from=<epoch_seconds_start>&until=<epoch_seconds_end>
```

Example: window of `2026-05-20 07:00:00 UTC` to `2026-05-28 06:59:59 UTC`:

```
?from=1779260400&until=1779951599
```

Note: the console URL uses **seconds**, not milliseconds — even though the MCP `extrahop_execute_metric_query` tool uses milliseconds for the same parameters. When converting from MCP query timestamps to URLs, divide by 1000.

**When to choose absolute over relative.** Default to relative — it matches what the operator wants 95% of the time ("show me what the report described, right now"). Switch to absolute when:

- The report header names a fixed window (`14:00–15:00 UTC on 2025-11-15`), not a rolling one.
- A scheduled run produced the report and the user may open it later, after the relative window has shifted past the data.
- An incident review pins the analysis to a specific outage window.

If unsure, relative is the safer default — by the time the operator clicks, the data they want is usually "the last N hours from now," not "the last N hours from when the report was written."

Omit `from`/`interval_type`/`until` only on the overview URL when no window is meaningful (rare — usually you do want the same window). If the user explicitly asked for a "current state" check without a window, default to `from=1&interval_type=HR&until=0`.

---

## Protocol slug table

Map the protocol from the finding to the URL slug. For application-layer protocols, the slug is the metric category with underscores replaced by hyphens. TCP and Network have their own slugs that don't follow the protocol naming.

| Finding refers to | Metric category | URL slug |
|---|---|---|
| HTTP, web tier | `http_server` / `http_client` | `http-server` / `http-client` |
| DNS server | `dns_server` | `dns-server` |
| DNS client / recursive | `dns_client` | `dns-client` |
| SMB / CIFS file server | `cifs_server` | `cifs-server` |
| LDAP server | `ldap_server` | `ldap-server` |
| Kerberos KDC | `kerberos_server` | `kerberos-server` |
| Database server | `db_server` | `db-server` |
| SSL / TLS server | `ssl_server` | `ssl-server` |
| TCP transport (retransmissions, RTO, flow stalls, RTT, setup time) | `tcp` | `tcp` |
| Network throughput, packet/byte volume, internal vs external | `net` | `network` |
| Generic / unspecified / multi-protocol / overall device health | — | `overview` |

**Default to `overview`.** The device overview is the right target whenever the report isn't pointing at one specific protocol — that includes mixed-protocol findings, overall health summaries, and any "investigate this device" call-to-action where the operator should land on the device's main page and choose where to look next.

**TCP vs Network.** Findings about retransmissions, RTOs, flow stalls (`rto_multi_*`), zero-windows, RTT, or setup time all go to `/tcp`. Findings about throughput, packet volume, or internal-vs-external traffic go to `/network`. When a single TCP-transport finding mentions both (e.g., "throughput dropped and retrans rose"), prefer `/tcp` since the retrans signal is usually the actionable one.

**Choosing client vs server.** Match the device's role in the finding. A DC flagged on Kerberos failures is `kerberos-server`. A workstation flagged on slow DNS resolution is `dns-client`. When unclear, prefer the side that drove the verdict (the side where errors or latency originated).

**Multi-protocol findings.** When a single bullet implicates two protocols (e.g., "LDAP + Kerberos both degraded on `dc-01`"), link to `overview` and let the operator drill in from there — don't pick one protocol arbitrarily.

---

## Formatting in the report

Wrap the backticked identifier with a Markdown link. The backticks stay; they hold for the identifier-typography rule.

- ✓ `` [`web-app-01`](https://...) ``
- ✗ `` `[web-app-01](https://...)` `` (link rendered as literal text inside the code span)
- ✗ `[web-app-01](https://...)` (loses the identifier typography)

Link only the **first occurrence** of an identifier in the body of the report. Repeat occurrences stay as plain backticked text. Exception: if "Drill in further" or "What to do" mentions an identifier that was already linked above, link it again there — those sections are skim-points and the user may not have read the body.

For device groups, link the group name the same way: `` [`HTTP Servers`](https://...) ``.

---

## Examples

These examples all use appliance UUID `7946be2a04354967a2ff79788087ee24` on host `revealx.example.com`. Both came from `extrahop_get_appliance_metadata`: the FQDN from `display_host`, the appliance UUID from `hostname`.

### Device overview, last 24 hours

Check on `web-app-01`, `discovery_id` `02bc5bb970bf0000`, window 24h:

```
https://revealx.example.com/extrahop/#/metrics/devices/7946be2a04354967a2ff79788087ee24.02bc5bb970bf0000/overview/?from=1&interval_type=DAY&until=0
```

### Device protocol page (SMB), last 7 days

Same device, finding about SMB server health, window 7d:

```
https://revealx.example.com/extrahop/#/metrics/devices/7946be2a04354967a2ff79788087ee24.02bc5bb970bf0000/cifs-server?from=1&interval_type=WK&until=0
```

### Device TCP transport page, last 1 hour

Finding about retransmissions and flow stalls on `web-app-01`, window 1h:

```
https://revealx.example.com/extrahop/#/metrics/devices/7946be2a04354967a2ff79788087ee24.02bc5bb970bf0000/tcp?from=1&interval_type=HR&until=0
```

### Device group, HTTP fleet, last 1 hour

Group ID 47, HTTP fleet check, window 1h:

```
https://revealx.example.com/extrahop/#/metrics/devicegroups/47/http-server?from=1&interval_type=HR&until=0
```

### Absolute time window (post-incident review)

Same device, SMB server page, fixed window of `2026-05-20 07:00:00 UTC` to `2026-05-28 06:59:59 UTC`:

```
https://revealx.example.com/extrahop/#/metrics/devices/7946be2a04354967a2ff79788087ee24.02bc5bb970bf0000/cifs-server?from=1779260400&until=1779951599
```

No `interval_type` is needed — the absolute timestamps (10-digit seconds) fully specify the window.

### In a finding bullet

```markdown
- **Degraded (new)** — *SMB server.* [`file-srv-01`](https://revealx.example.com/extrahop/#/metrics/devices/7946be2a04354967a2ff79788087ee24.02bc5bb970bf0000/cifs-server?from=1&interval_type=WK&until=0) is rejecting 8% of SMB requests with STATUS_ACCESS_DENIED, sustained across the window.
```

The reader sees the identifier in backticks, can click straight to the SMB protocol page for that device at the assessment window, and skip the manual navigation steps.

---

## Safeguards

- **Never fabricate.** No guessing the appliance UUID, hostname, or discovery_id. If `extrahop_get_appliance_metadata` is unavailable and you can't get the FQDN another way, emit the report unlinked and move on. Better unlinked than wrong-linked. Remember the `extrahop_get_appliance_metadata` field mapping: FQDN from `display_host`/`external_hostname`, appliance UUID from `hostname`, never `mgmt_ipaddr`.
- **One window per report.** All URLs in a single report use the same `from`/`interval_type` — the one that matches the assessment window. Mixing windows confuses the reader.
- **Don't link metric names or threshold values.** Only identifiers (devices, device groups, applications) and the occasional "open the console" call-to-action.
- **Don't substitute URLs for explanation.** The finding still has to be readable on its own. Someone reading the report on a phone in a meeting shouldn't need to tap a link to know what's broken.
- **Sensitive environments.** If the user's environment is internal-only and they've indicated the report may be shared (PDF export, paste into a ticket), still include the URLs — they're harmless to recipients without console access, and useful to recipients who do.
