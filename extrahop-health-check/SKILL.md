---
name: extrahop-health-check
description: Run accurate, role-aware network and service health checks against an ExtraHop RevealX environment. Use whenever the user asks about the state of their network, application performance, infrastructure health, IT operations status, or root-cause analysis — including phrasings like "what's wrong with the network," "investigate this device," "check DNS/HTTP/Kerberos/LDAP/SMB/database health," "is the network healthy," "are users complaining," or "run a health check." Also use proactively when the user describes symptoms (slow site, login issues, timeouts, file share problems, TCP retransmissions, packet loss, dropped connections, authentication failures, certificate issues, account lockouts) in an ExtraHop-monitored environment. Activate even without the words "health check" — if the question is about the state of network services or application performance in an ExtraHop environment, this skill applies. Requires an ExtraHop MCP server connected (any AI client supported).
---

# ExtraHop Network Health Check

Tools are named with the `extrahop_` prefix below (e.g. `extrahop_search_devices`). If your client namespaces MCP tools by server, prefix accordingly (e.g. `ServerName:extrahop_search_devices`).

## Reference files

- **`reference/domain-knowledge.md`** — thresholds, error classification rules, freshness gate, activity gates, baseline selection, role weighting, HSI bucketing, TCP math, sensor caveats. Load whenever running a check.
- **`reference/output-templates.md`** — output format (Default and Detailed modes), NEW/CHRONIC modifier, bimodal fleet rule, stale-data handling, continuation prompt, worked examples. Load before emitting your report.
- **`reference/html-report.md`** — the branded, self-contained HTML report deliverable (opt-in third output mode). Load when the user asks for an artifact — "HTML," "PDF," "shareable," "deliverable," "one-pager," "export," or "for leadership" (the word "report" alone is not an HTML trigger; see Mode selection under Output).
- **`reference/diagnostic-playbooks.md`** — multi-tier root-cause recipes. Load when a category flags Warning or Degraded.
- **`reference/console-urls.md`** — how to construct deep-links into the RevealX console (device pages, protocol pages, device groups) at the right time window. Load before emitting any default-mode report that names a device or device group.
- **`reference/scheduling.md`** — per-client recipes for recurring runs. Load only when the user asks about scheduling.

## Scope

Infer from the user's request:

| Scope | Trigger | What it does |
|---|---|---|
| **Environment** | No target named, or "the network / overall health" | Capture-level screening across sensors, then drill into flagged protocols |
| **Device** | Device names, IPs, or applications mentioned | Resolve target, assess all relevant protocols + TCP + latency, role-weighted |
| **Protocol** | A protocol named without a device | Capture screening, then fleet discovery and sampled drill-down |

If ambiguous, default to environment and ask after the report whether to drill into a device or protocol.

**Companion skill.** This is the network/service *performance* half of the ExtraHop RevealX skill bundle. For *security* work — triaging NDR detections, separating false positives from real threats, reconstructing attack chains, or opening investigation cases — use the `extrahop-triage` skill instead. If a health check on a device surfaces a security concern (e.g. an account-lockout spike that looks like a password spray), hand off to `extrahop-triage`.

Modifiers parsed from natural language: time window (`1h`, `6h`, `24h`, `7d`), comparison window (`compare to last week`), protocol focus on a device (`focus on TCP`).

**Tagging mode** activates when the user says "tag the results," "mark the unhealthy ones," "persist as tags," or passes `--tag`.

## Prerequisites

Required MCP tools: `extrahop_search_devicegroups`, `extrahop_search_devices`, `extrahop_get_device`, `extrahop_execute_metric_query`, `extrahop_search_metric_catalog`, `extrahop_search_records`.

For tagging mode: pre-existing tags `Health-Warning` and `Health-Degraded`, plus `extrahop_assign_devicetag_to_devices` / `extrahop_unassign_devicetag_from_devices`.

For console deep-links: `extrahop_get_appliance_metadata` supplies both the console FQDN (its `display_host` / `external_hostname` fields) and the appliance UUID (its `hostname` field) used to build URLs. If it's absent (older MCP server), the skill omits links rather than guessing — see Console Deep-Links.

If a required tool is missing, say so and proceed with what's available.

## Core Methodology

### 1. Two-pass error classification

Never classify a protocol Warning/Degraded from raw `rsp_error`. Always:

1. Query aggregate `rsp_error` (Pass 1).
2. Query the breakdown metric (Pass 2) to separate actionable from benign.
3. Compute status from the actionable rate.

Breakdown metrics and benign error filters (full table in `domain-knowledge.md`):

- HTTP: `http_server:status_code` — only 5xx is actionable
- DNS: `dns_server:rsp_rcode` — only SERVFAIL + FORMERR is actionable
- Kerberos: `kerberos_server_detail:error_msg` — `KDC_ERR_PREAUTH_REQUIRED` is benign
- LDAP: `ldap_server:error_msg_short` — `referral` and `noSuchObject` are benign

### 2. Evidence sufficiency

Before issuing any verdict above Normal, verify all four:

- **Freshness.** Most recent capture-level data < 5 min old. If > 10 min stale, return Insufficient Evidence (see "Stale Data Handling" in `output-templates.md`).
- **Minimum activity.** ≥100 responses for HTTP/DNS/LDAP/Kerberos/CIFS/DB; ≥1000 connections or ≥100K packets for TCP retransmissions.
- **Baseline validity.** Baseline window doesn't cross a maintenance/weekend boundary the assessment window doesn't; baseline itself ≥100 responses.
- **Asymmetric routing.** `tcp:unidirectional_flows` < 25% of total flows on the sensor. Above 25%, don't issue TCP-based verdicts.

If any check fails for a category that would have driven the verdict, downgrade to Insufficient Evidence.

### 3. Silent outage detection (volume-drop)

Errors aren't the only failure signal. A service that has gone silent produces zero errors on (nonexistent) traffic. Always check request volume vs baseline:

- > 5× drop sustained across window → Degraded — silent outage, even with normal error rates.
- > 5× rise → load event; check whether peers are absorbing the shift.

### 4. Multi-tier correlation

Before finalizing Warning/Degraded on any category, check whether the cause is downstream:

- HTTP 5xx → check backend DB latency and TCP retransmissions on web→db links
- LDAP errors on a DC → check Kerberos and replication on the same DC (single AD finding, not two)
- SMB slowness → check `tcp:rto_out` and `zwnd_in` on the file server first
- DB latency → check TCP layer first; if clean, likely DB/storage (out-of-band)

When a downstream cause is found, upstream verdict still reflects user experience but the report's recommended actions target the downstream tier. Promote the downstream device as a first-class drill-down, not buried in prose. Full playbooks in `diagnostic-playbooks.md`.

### 5. Baseline comparison

Compare current to prior equivalent period. For windows ≥ 24h, prefer same-day-last-week. For low-volume devices, prefer peer comparison.

Meaningful deviation requires all three: percentage change > 2× AND absolute difference exceeds the activity threshold AND baseline itself ≥ activity gate. The third rule prevents reports like "errors up 233% (3 → 10)."

### 6. NEW vs CHRONIC modifier

After computing the current verdict, run the same assessment on the baseline window and compare verdicts:

- Same verdict as prior period → `(chronic)` (existing performance debt, not an on-call event)
- Worse than prior → `(new)` (this week's problem, likely worth investigating)
- Better than prior → `(recovered)`

Omit the modifier when prior-period data is unavailable or below the activity gate. Apply in the verdict line and on individual findings bullets.

### 7. Temporal pattern analysis

Use `bucketing: "timeseries"` to distinguish sustained from transient:

- Sustained (> 50% of buckets): full severity
- Transient (< 20%): reduce severity by one level
- Intermittent (20–50%): report at aggregate severity with note
- Step change: note transition time, report post-change severity

### 8. Health Satisfaction Index (HSI)

Computed internally for verdict calibration and trend tracking. Not displayed in default mode. Full methodology in `output-templates.md`.

### 9. Latency assessment

Primary indicator: `tprocess` (Server Processing Time). Always request percentiles bracketing T and 4T — typically `[10, 25, 50, 75, 90, 95, 99]`. Workload type drives threshold selection: OLTP vs OLAP for DB, application vs static for HTTP. See `domain-knowledge.md` → Workload Inference.

### 10. TCP retransmissions

Two formulas with distinct semantics. Prefer Form B when `pkts_out` is available.

- **Form A — events per connection:** `(rto_out + retrans_out) / (connected + accepted)`. Not a percentage. Thresholds: < 0.5/conn normal, 0.5–2 warning, > 2 degraded.
- **Form B — per-packet rate:** `rto_out / pkts_out`. True probability. Thresholds: < 0.1% normal, 0.1–1% warning, > 1% degraded.

When the two disagree (Form A high, Form B low), it indicates long-lived connections — the path is fine, the workload pattern is unusual. Report this as a workload finding, not a transport finding.

## Health Check Procedures

### Pre-check (all scopes)

Run the freshness gate before anything else. Query `net:bytes` at capture level for the most recent 5-minute bucket. If > 10 min stale, return Insufficient Evidence immediately.

### Environment

1. **Discover** sensors via `extrahop_search_devicegroups`.
2. **Capture-level screening** per sensor (`object_type: "capture"`): `app:bytes` topn, protocol error+volume aggregates, `tcp:desync`, `tcp:unidirectional_flows`, baseline for comparison.
3. **Evidence sufficiency** for each non-trivial protocol.
4. **Volume-drop scan.** Flag any > 5× drop (silent outage) or > 5× rise (load event).
5. **Device drill-down** only for protocols flagged by errors OR volume drop: discover by role; two-pass classification on top 5–10 devices; TCP transport; latency percentiles.
6. **HSI** per category, per device, fleet (sample-weighted).
7. **Multi-tier correlation** on any Warning/Degraded.
8. **Emit report** per `output-templates.md`.

### Device

1. **Resolve** via `extrahop_search_devices`; capture role via `extrahop_get_device` if needed.
2. **Workload inference** for DB/HTTP before applying latency thresholds.
3. **Query** all relevant protocol categories (with `_server`/`_client` suffix) + TCP transport + latency percentiles.
4. **Baseline.** Same-day-last-week for windows ≥ 24h, else prior equivalent. Add peer baseline for low-volume devices.
5. **Volume-drop check** alongside errors and latency.
6. **Two-pass classification** for each protocol with errors.
7. **Activity gates and temporal pattern.**
8. **HSI** per primary category, aggregate device HSI.
9. **Role weighting** — primary vs secondary (see `domain-knowledge.md`).
10. **Multi-tier correlation** if any category is Warning/Degraded; promote downstream root cause as a first-class drill-down.
11. **Emit report.**

### Protocol fleet

1. **Capture-level screening** across all sensors (errors + volume).
2. **Discover** fleet via `extrahop_search_devices` by role.
3. **Workload inference** per device (especially DB OLTP vs OLAP).
4. **Device assessment** on a sample of up to 10, with two-pass, volume check, HSI.
5. **Peer comparison.** Each device vs fleet median; outliers via MAD test.
6. **Fleet HSI** sample-weighted; check for bimodal distribution.
7. **Emit report** ranking devices by HSI ascending; call out fleet-wide vs localized.

## Tagging Mode

For each device assessed at device level:

1. Clear stale tags: `extrahop_unassign_devicetag_from_devices` for both `Health-Warning` and `Health-Degraded`.
2. If Degraded → assign `Health-Degraded`.
3. If Warning → assign `Health-Warning`.
4. If Normal or Insufficient Evidence → no tag (step 1 already cleared).

Only devices assessed at device level get tagged — not those passing capture-level screening unexamined. Named device in device-scope checks always gets tagged. Tags must pre-exist; report errors but continue.

Interactive: confirm before applying. Headless/scheduled: apply and report. If unclear, ask.

Include a TAGGING SUMMARY in the report showing devices tagged, devices cleared, and any errors.

## Tool Strategy

| Purpose | Tool | Notes |
|---|---|---|
| Discover sensors | `extrahop_search_devicegroups` | First step in environment/protocol checks |
| Enumerate a device group | `extrahop_list_devices_in_devicegroup` | Resolve members of a known group for fleet/sensor work |
| Find metric names | `extrahop_search_metric_catalog` | When unsure of exact stat_name |
| Collect metrics | `extrahop_execute_metric_query` | Always `cycle: "auto"` |
| Resolve devices | `extrahop_search_devices` | By name, IP, role, tag |
| Device details | `extrahop_get_device` | When you have OID, need role/name |
| Transaction drill-down | `extrahop_search_records` | Only on sustained Warning/Degraded; max 7d |
| Apply / remove tags | `extrahop_assign_devicetag_to_devices` / `extrahop_unassign_devicetag_from_devices` | Tagging mode only |
| Get console FQDN + UUID | `extrahop_get_appliance_metadata` | For deep-links; FQDN from `display_host`/`external_hostname`, appliance UUID from `hostname`. Absent on older servers → omit links |

Query patterns:

- **Capture screening:** `object_type: "capture"`, bare category names, `bucketing: "total"`.
- **Device latency for HSI:** `object_type: "device"`, `_server` suffix, `calc_type: "percentiles"`, `[10, 25, 50, 75, 90, 95, 99]`.
- **Temporal analysis:** `bucketing: "timeseries"`, `cycle: "auto"`.
- **Volume tracking:** query `:rsp` alongside `:rsp_error` for volume-drop detection.

Start broad at capture level. Only drill into device level where capture-level screening flagged something (by errors OR volume drop). Batch metric_specs in single `extrahop_execute_metric_query` calls.

`extrahop_search_records` is expensive and bounded to 7-day retention. Drill in only when a category is Degraded, OR Warning with sustained pattern (>50% of buckets), AND window ≤ 7d. Or when the user explicitly asks.

## Output

See `output-templates.md` for the full format spec. Two chat modes:

- **Default mode** — interactive checks. H2 title, bold verdict line, one-sentence problem statement, verdict-first findings bullets, "Key insight." paragraph, "What to do" / "Drill in further" sections. No HSI displayed, no confidence line, no YAML footer. Identifiers in backticks. Fits one screen of chat.
- **Detailed mode** — scheduled runs, audits, tagging, explicit-request, or programmatic consumer. Verbose format with HSI, confidence, "What changed" table, structured per-category subsections, YAML footer.

Default mode is correct for almost all interactive checks.

A third, opt-in **HTML report mode** produces a branded, self-contained, PDF-ready HTML deliverable — see `reference/html-report.md`. It is a branded **export of the Default-mode chat report**: same target, verdict (shown as a status tag in the masthead), findings, Key insight, and next-step lists, wrapped in an ExtraHop masthead and print styling. It does not add tables, Root Cause/Evidence/Limits sections, HSI, or confidence lines — Default mode omits those, so the export does too. Copy `assets/report-template.html` byte-for-byte (the `<style>` block ships unmodified), fill the marked regions with the same facts you'd put in the chat report, and write the file to the workspace root as `health-check-<scope-slug>-<date>.html`. Every guardrail below applies identically to the assessment behind it — freshness gate, two-pass classification, evidence sufficiency, silent-outage check, NEW/CHRONIC, never-fabricate. When freshness fails or evidence is insufficient, prefer the Markdown refusal over a branded verdict (a branded page makes fabricated telemetry look more authoritative, so the bar is higher, not lower).

**Mode selection — explicit precedence (apply top-down, first match wins):**

1. **HTML report mode** — only for **artifact-oriented** requests: the words "HTML," "PDF," "shareable," "deliverable," "one-pager," "export," "for leadership/execs," or the `--report` flag. These name a *file to hand off*. **If the user asked for a PDF specifically, the HTML alone does not satisfy the request — also render it to PDF** (see "PDF delivery" in `html-report.md`); only if no renderer is available do you deliver the print-ready HTML with instructions, and say so explicitly.
2. **Detailed mode** — for requests asking for **more content/structure in chat**: "the full report," "detailed view/report," "structured data," "everything," plus all scheduled / tagging / downstream-agent runs. These want the verbose Markdown (HSI, tables, YAML), not a file.
3. **Quick-look** — "tldr," "is everything okay," "headline."
4. **Default mode** — everything else, including a bare "report me a health check" with no artifact or detail cue.

The word **"report" alone is NOT an HTML trigger** — it's ambiguous, so it falls through to Default (or to Detailed if paired with "full"/"detailed"). Require an explicit artifact term for HTML. If a request combines cues (e.g. "detailed PDF"), the artifact term wins → HTML (an HTML export whose underlying assessment is complete). When genuinely unclear whether the user wants a file or richer chat, ask rather than guess.

Critical rules across all modes:

- **Status vocabulary:** `Normal`, `Warning`, `Degraded`, `Insufficient Evidence` (uppercase in YAML).
- **Stale data refusal:** when freshness fails, the report IS the freshness warning. Don't bury staleness in a confidence caveat.
- **Quick-look mode:** for "tldr" / "is everything okay" / "headline only," collapse to title + verdict line + one sentence + offer to elaborate.
- **Continuation prompt:** for Warning/Degraded/Insufficient-Evidence reports in default mode with 2+ chat-actionable drill-downs and an interactive context, offer the drill-downs as a follow-up choice. If your client exposes an interactive prompt/choice primitive (tappable options), use it; otherwise present the same options as a short plain-text list ending the turn. Always include an escape hatch. Skip on Normal, detailed mode, headless/scheduled, tagging mode.

## Console Deep-Links

When the report names a device or device group, wrap that identifier in a Markdown link to the corresponding page in the RevealX console at the assessment time window. This turns the report into a launchpad — the operator clicks the identifier and lands on the right protocol page, scoped to the right window, instead of navigating manually.

Required inputs: the **console FQDN** (e.g. `revealx.example.com`) and, for device URLs only, the **appliance UUID** (32-hex string).

Both come from the **`extrahop_get_appliance_metadata`** tool — call it once per session and cache the result. Read the **FQDN** from the `display_host` field (fall back to `external_hostname`), and the **appliance UUID** from the `hostname` field. Note the field names are counter-intuitive: `hostname` holds the 32-hex appliance UUID, *not* the FQDN, and `mgmt_ipaddr` is the management IP — never use either as the FQDN. **If `extrahop_get_appliance_metadata` is not available (the user is on an older MCP server that doesn't expose it) and you can't obtain the FQDN another way, do not construct any links** — emit the report with plain backticked identifiers. A correct unlinked report is strictly better than a fabricated one. Never fabricate the FQDN or the UUID.

When `extrahop_get_appliance_metadata` is unavailable, the fallback is a console URL the user pasted earlier (its `/metrics/devices/<32hex>.<16hex>/` path yields both the FQDN and the appliance UUID) or prior session memory. Device-group URLs need only the FQDN; device URLs additionally need the UUID — when it isn't available, skip the device-level link rather than guessing it. Cache both pieces for the session.

Apply in default mode only: the problem statement and findings bullets (first mention of each identifier), "What to do" actions naming a device, "Drill in further" items, and Key insight (only if not already linked above). Skip in detailed mode YAML, stale-data refusals, quick-look mode, and tagging-mode reports.

Full URL syntax, time-parameter mapping, protocol slug table, and worked examples in `console-urls.md`.

## Scheduling

For recurring runs (every 4 hours, daily, weekly), see `scheduling.md` — covers Claude Code, Claude Desktop, Claude.ai, GitHub Copilot, Gemini CLI, and generic agents.

## Principles

1. **Accuracy over sensitivity.** Better Normal than a false flag.
2. **Two-pass classification is mandatory.** Never assess from raw `rsp_error`.
3. **Trust the engineer.** State findings plainly with the one or two numbers that matter. Confidence levels, HSI percentages, baselines, and threshold quotes belong in detailed mode and the YAML footer.
4. **NEW vs CHRONIC matters more than verdict alone.** Compare to prior-period verdict and mark the difference visibly.
5. **Root-cause oriented.** Don't stop at symptoms. Promote downstream devices as first-class drill-downs.
6. **Silent failures matter.** Zero errors on zero traffic isn't healthy.
7. **Fresh data only.** When freshness fails, the report IS the warning.
8. **Bimodal honesty.** When a fleet has wide HSI spread, lead with the shape ("12 healthy + 3 degraded"), not the misleading average.
9. **Role-aware.** A DC's health is Kerberos/LDAP/DNS, not its HTTP management console.
10. **Concise.** A default-mode report fits one screen of chat. If longer, you're over-reporting — move detail to detailed mode.
11. **Never fabricate data.** Report only what the tools return — never invent devices, IPs, hostnames, metric values, percentages, baselines, timestamps, or console URLs. If a query is truncated or sampled, say so and scope the claim to what was seen. When evidence is missing, return Insufficient Evidence; do not fill the gap with a plausible-looking number. Fabricated telemetry is worse than no answer — and worse still inside a branded HTML report, which lends unearned authority to any invented number.
