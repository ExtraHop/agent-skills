# Console URL Construction

Embed deep-links into the RevealX console so the user can jump from a finding to the exact protocol page and time window in one click. The chat session is the diagnosis; the console is where they take it forward.

---

## When to construct URLs

Build a URL whenever the report names a device group. Specifically:

- **Findings bullets** — link the device group identifier the first time it appears in a finding bullet. When the finding is about a specific protocol on that group (HTTP, DNS, SMB, etc.), point at the protocol page, not the overview. When the bullet is about overall group health or there's no single dominant protocol, point at the overview.
- **Drill in further** — any item that names a device group should link to the relevant console page (overview, or the protocol that matters).
- **What to do** — when the action names a device group, link the identifier to its overview page.
- **Key insight** — link identifiers the first time they appear if they weren't already linked above. Don't double-link the same identifier in the same report.

Skip URLs in:

- **Detailed mode YAML footer.** Identifiers there are for machine parsing.
- **Stale data refusal reports.** The console can't show data that doesn't exist; sending the user there is hostile.
- **Quick-look mode.** Intentionally minimal.
- **Tagging mode reports.** Operator-facing summary, not investigation.

---

## Prerequisite: hostname

Every console URL needs the console FQDN.

- **Console FQDN** (e.g. `revealx.example.com`) — the customer's RevealX hostname. Forms the URL base: `https://<fqdn>/extrahop/#/`. Obtained from the `extrahop_get_appliance_metadata` tool (see Acquisition order below).

The `extrahop_get_appliance_metadata` tool returns the console FQDN:

| Field | Holds | Use for |
|---|---|---|
| `display_host` | The console FQDN (e.g. `revealx.example.com`) | **FQDN** — primary source |
| `external_hostname` | Usually the same FQDN | **FQDN** — fallback if `display_host` is empty |
| `mgmt_ipaddr` | Management IP | Never use for URLs |

Acquire the FQDN **once per session**, then cache and reuse.

### Acquiring the FQDN

1. **Call `extrahop_get_appliance_metadata`.** Read the **FQDN** from `display_host` (fall back to `external_hostname`). If the response is missing `display_host`/`external_hostname`, do not substitute `hostname` or `mgmt_ipaddr` — treat the FQDN as unavailable. Call it once and cache the FQDN for the rest of the session.

2. **(Fallback) Parse a URL the user already pasted** in this conversation, matching the pattern `https://<fqdn>/extrahop/#/...`. Use this only if `extrahop_get_appliance_metadata` is unavailable or returned no usable FQDN.

3. **No FQDN → no links.** If `extrahop_get_appliance_metadata` is unavailable (the user is on an older MCP server that doesn't expose it) and no FQDN is available another way, **do not construct any links.** Emit the report with plain backticked identifiers. A correct unlinked report is strictly better than a fabricated one. Do not guess the hostname.

### Caching

Cache the FQDN for the rest of the session as soon as you have it. Don't re-call `extrahop_get_appliance_metadata` per finding. If the user opens a new session, you'll re-acquire — that's fine, it's one tool call.

### Never fabricate

- Never invent the FQDN. Plausible-looking domains (`acme.extrahop.com`, `customer.cloud.extrahop.com`) are a trap — a wrong host sends the operator to an unrelated tenant's data or to a 404. Worse, in shared-screen demos a wrong FQDN can leak the existence of other customers. If you have no FQDN, emit the report unlinked.
- Never use the **management IP** (`mgmt_ipaddr`) as the FQDN. Most modern deployments require the FQDN for cert validation, and an IP-based URL may not resolve to the console UI at all. Only use the IP if the user explicitly says that's their access path.

---

## URL syntax

### Device group pages

```
https://<hostname>/extrahop/#/metrics/devicegroups/<group_id>/<protocol-slug>?from=<N>&interval_type=<UNIT>&until=0
```

`group_id` is the integer returned by `extrahop_search_devicegroups` as `id`.

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
| Generic / unspecified / multi-protocol / overall group health | — | `overview` |

**Default to `overview`.** The group overview is the right target whenever the report isn't pointing at one specific protocol — that includes mixed-protocol findings, overall health summaries, and any "investigate this group" call-to-action where the operator should land on the group's main page and choose where to look next.

**TCP vs Network.** Findings about retransmissions, RTOs, flow stalls (`rto_multi_*`), zero-windows, RTT, or setup time all go to `/tcp`. Findings about throughput, packet volume, or internal-vs-external traffic go to `/network`. When a single TCP-transport finding mentions both (e.g., "throughput dropped and retrans rose"), prefer `/tcp` since the retrans signal is usually the actionable one.

**Choosing client vs server.** Match the device's role in the finding. A DC flagged on Kerberos failures is `kerberos-server`. A workstation flagged on slow DNS resolution is `dns-client`. When unclear, prefer the side that drove the verdict (the side where errors or latency originated).

**Multi-protocol findings.** When a single bullet implicates two protocols (e.g., "LDAP + Kerberos both degraded in `Domain Controllers`"), link to `overview` and let the operator drill in from there — don't pick one protocol arbitrarily.

---

## Formatting in the report

Wrap the backticked identifier with a Markdown link. The backticks stay; they hold for the identifier-typography rule.

- ✓ `` [`HTTP Servers`](https://...) ``
- ✗ `` `[HTTP Servers](https://...)` `` (link rendered as literal text inside the code span)
- ✗ `[HTTP Servers](https://...)` (loses the identifier typography)

Link only the **first occurrence** of an identifier in the body of the report. Repeat occurrences stay as plain backticked text. Exception: if "Drill in further" or "What to do" mentions an identifier that was already linked above, link it again there — those sections are skim-points and the user may not have read the body.

For device groups, link the group name the same way: `` [`HTTP Servers`](https://...) ``.

---

## Examples

### Device group, HTTP fleet, last 1 hour

Group ID 47, HTTP fleet check, window 1h:

```
https://revealx.example.com/extrahop/#/metrics/devicegroups/47/http-server?from=1&interval_type=HR&until=0
```

---

## Safeguards

- **Never fabricate.** No guessing the hostname. If `extrahop_get_appliance_metadata` is unavailable and you can't get the FQDN another way, emit the report unlinked and move on. Better unlinked than wrong-linked. Remember the `extrahop_get_appliance_metadata` field mapping: FQDN from `display_host`/`external_hostname`, never `mgmt_ipaddr`.
- **One window per report.** All URLs in a single report use the same `from`/`interval_type` — the one that matches the assessment window. Mixing windows confuses the reader.
- **Don't link metric names or threshold values.** Only identifiers (device groups, applications) and the occasional "open the console" call-to-action.
- **Don't substitute URLs for explanation.** The finding still has to be readable on its own. Someone reading the report on a phone in a meeting shouldn't need to tap a link to know what's broken.
- **Sensitive environments.** If the user's environment is internal-only and they've indicated the report may be shared (PDF export, paste into a ticket), still include the URLs — they're harmless to recipients without console access, and useful to recipients who do.
