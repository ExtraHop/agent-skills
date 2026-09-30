# Output Templates and Worked Examples

Two output modes: **Default** (interactive) and **Detailed** (scheduled / audit / explicit request). Default is correct for almost all interactive checks.

---

## Default Mode

### Format

```markdown
## Health Check: <target>

**<Verdict>** · <Time window> · <scope qualifier if useful>

<one-sentence problem statement in plain English; for healthy reports, one sentence stating that>

**Findings**

- **<Verdict>** — *<Category>.* <one-sentence finding in plain English>
- **<Verdict>** — *<Category>.* <one-sentence finding>
- **<Verdict>** — *<Category>.* <one-sentence finding>

**Key insight.** <one paragraph: what's happening, what was ruled out, what's still healthy.>

**What to do**

- <Operator action outside the chat>

**Drill in further**

- <Follow-up the user can paste back into chat>
```

### Rules

**Title.** `## Health Check: <target>` — H2, not H1.

**Verdict line.** `**<Verdict>** · <Time window>` directly under the title. Middle-dot separator (`·`). Add scope qualifiers when useful (`· 3 sensors`, `· 19 servers`). When the verdict has a NEW/CHRONIC modifier, include it: `**Degraded (new)**`.

**Verdict vocabulary.** `Normal` · `Warning` · `Degraded` · `Insufficient Evidence`. Title case in visible output; uppercase in YAML. Modifiers `(new)`, `(chronic)`, `(recovered)` per "NEW vs CHRONIC."

**Problem statement.** One sentence in plain English. Identifiers (`web-app-01`, `ldap-hq-1.corp.example.com`) earn their place; metric names and threshold values don't. For healthy reports, state plainly: "All sensors and protocols are within normal ranges."

**Findings bullets.** This is the core scannable element.

- Lead with the verdict word in bold. Non-negotiable — this is what makes the list scannable.
- Italicize the category in sentence case (`*HTTP latency*`).
- Em-dash + period after category, then the finding: `- **Normal** — *DNS.* Resolution times normal.`
- One sentence per finding. Longer explanation goes in Key insight.
- Sub-bullets are OK for structured detail (per-server breakdowns). Use sparingly.
- Cap at 4–6 findings. Include only categories that earn their place: degraded/warning always; normal only when ruling them out is operationally useful, or when omitting them would mislead.

**Key insight.** Short paragraph. Lead with `**Key insight.**` as a sentence opener (period, not colon — not a heading). Tell the story: what's happening, what was ruled out, what's still healthy. Three or four sentences. Specific numbers earn their place when they support the conclusion; don't dump percentile tables. No threshold quotes. No metric names — use display names ("server processing time" not `tprocess`, "flow stalls" not `rto_multi_out`). No acronyms without explanation.

**What to do / Drill in further.** Bold inline labels, not H2 headings. Plain bullets — no emoji or special icons. The section label carries the distinction:

- **What to do** — operator actions outside the chat.
- **Drill in further** — follow-up questions the user can paste back.

Omit **What to do** entirely on healthy reports. Cap each section at 3–4 items.

### Do not include in default mode

- HSI percentages (computed but not displayed)
- Confidence lines (fold Medium/Low into Key insight as a qualifier)
- Scope/time/HSI block under the title
- "What changed" vs "What's steady" sub-sections (the bullets already do this)
- YAML footer
- Structured fields under categories

### Typography

- **Identifiers in backticks.** Device names, hostnames, IPs, metric names. The single most important typography rule.
- **Magnitudes:** `1.4s` not `1400ms` once ≥ 1s. `142 GB` not bytes. `2.3%` not `0.023`.
- **Time format:** relative + local TZ ("Last 24 hours"). UTC anchor only in YAML.
- **No fake alignment.** Don't pad with whitespace; Markdown can't right-justify.

### Length target

One screen of chat. Title + verdict line + problem sentence + 4–6 findings + 3–5 sentence Key insight + 3–5 next-step items. If longer, move detail to Key insight prose or detailed mode.

---

## Worked Examples — Default Mode

### Example 1: Device check with multi-tier root cause (Degraded, new)

```markdown
## Health Check: web-app-01

**Degraded (new)** · Last 1 hour

HTTP 5xx errors are elevated on `web-app-01`, but the root cause is database latency on `db-prod-02` — not the web tier itself.

**Findings**

- **Degraded (new)** — *HTTP responses.* 2.3% of responses returning 5xx (baseline 0.3%), sustained across the full hour. Step change at 14:22 UTC.
- **Warning (new)** — *HTTP latency.* Server processing time p95 climbed from 180ms baseline to 1.4 seconds, coincident with the 5xx rise.
- **Degraded (new)** — *Backend dependency.* Outbound TCP to `db-prod-02` shows 4× the baseline RTO rate. Database server processing time p95 on `db-prod-02` has risen from 80ms to 1.2s.
- **Normal** — *TCP transport (local).* RTT and setup times normal. The issue is not at the network layer on `web-app-01` itself.

**Key insight.** The 5xx errors on `web-app-01` are real and impacting users (≈285 affected sessions/hour based on observed request volume), but the cause is one tier down. `db-prod-02` became slow at 14:22 and `web-app-01`'s responses are timing out waiting on it. Other web tier members (`web-app-02`, `web-app-03`) are healthy because they're load-balancing onto `db-prod-01`, not `db-prod-02`. The web tier doesn't need attention — the database does.

**What to do**

- Page database on-call. Investigate `db-prod-02` for long-running queries, replication lag, or storage I/O around 14:22 UTC.
- If `db-prod-02` must be removed from rotation, verify `db-prod-01` capacity headroom first.

**Drill in further**

- Run a full health check on `db-prod-02`
- Show database transactions on `db-prod-02` with response time > 1 second
```

### Example 2: Fleet check with bimodal distribution (Degraded, new)

```markdown
## Health Check: HTTP Fleet — 19 web servers

**Degraded (new)** · Last 7 days

Most of the fleet is healthy, but 3 servers are newly degraded this week with material user impact. Zero HTTP errors fleet-wide — this is purely a latency problem.

**Findings**

- **Normal** — *HTTP errors.* Zero 5xx responses across all 19 servers and 647K total responses.
- **Degraded (new)** — *HTTP latency.* Three servers newly degraded:
  - `web-edge-03.dc1` — response time p99 of 2.2s
  - `web-api-02.dc1` — p99 of 1.6s
  - `web-api-03.dc1` — p99 of 0.55s, up from 53ms last week
- **Warning (new)** — *Workload.* TCP transport is clean on 18 of 19 servers. `web-edge-03` shows 6 flow stalls and heavy retransmissions on long-lived high-throughput connections (15K packets/sec sustained). Per-packet retrans rate is fine — the path is healthy; the workload pattern is the signal.
- **Warning (chronic)** — *Performance debt.* Four servers (`web-legacy-00`, `web-legacy-01`, `web-static-00`, `Device-0a1b2...`) sit at p95 ~290–400ms. Same as last week and the week before.

**Key insight.** Twelve of 19 servers are healthy. The three newly-degraded servers split into two patterns. `web-edge-03` has more than doubled its traffic and is showing flow stalls on long-lived connections — the network is fine, the workload is congesting it. `web-api-02` and `web-api-03` have clean TCP but server-side latency regressions, and they share a naming pattern that suggests common infrastructure — investigate them together. The four chronically-slow servers are performance debt, not new findings.

**What to do**

- Investigate `web-edge-03`: verify the +153% traffic surge is intended; identify the workload causing flow stalls.
- Investigate `web-api-02` server-side — CPU, application logs, downstream dependencies. TCP is clean, so cause is local.
- Correlate deployment history of `web-api-02` and `web-api-03` — simultaneous degradation with shared naming suggests a common change.

**Drill in further**

- Show top HTTP URIs and methods on `web-edge-03` over the last 24 hours
- Run a health check on `web-api-02` and `web-api-03` together
```

### Example 3: Healthy environment

```markdown
## Health Check: Environment

**Normal** · Last 24 hours · 3 sensors

All sensors and protocols are within normal ranges. No degradation detected.

**Findings**

- **Normal** — *HTTP.* All web tier members healthy. Per-server processing times within baseline.
- **Normal** — *DNS.* Resolution times normal. Some NXDOMAIN traffic from AD discovery (benign).
- **Normal** — *LDAP / Kerberos.* Domain controller authentication services operating within normal latency.
- **Normal** — *TCP transport.* No flow stalls, retransmission rates negligible across all sensors.

**Key insight.** No protocol category exceeded its warning threshold after error reclassification. DNS raw error rate was elevated at 3.1% on `dc-west`, but 96% of those were NXDOMAIN — typical AD discovery and reverse-lookup traffic — leaving an actionable rate of 0.12%. Request volume is within 8% of last week's same-day, consistent with normal weekday traffic. No silent outages detected.

**Drill in further**

- Show the busiest protocols by traffic volume over the last 24 hours
- Run a protocol fleet check on DNS to see per-server breakdowns
```

### Example 4: Silent outage (volume-drop)

```markdown
## Health Check: DNS Recursive Servers — 2 hosts

**Degraded (new)** · Last 1 hour

`dns-recursive-01` has effectively stopped serving traffic — request volume dropped 94% from baseline with no error increase. `dns-recursive-02` is absorbing the displaced load and is now a single point of failure.

**Findings**

- **Degraded (new)** — *`dns-recursive-01` volume.* Handled 1,840 responses this hour versus 31,200 baseline (down 94%). Sustained across every minute of the window.
- **Normal** — *`dns-recursive-02` volume.* Absorbed displaced load: 54,500 responses versus 29,400 baseline (up 85%).
- **Normal** — *DNS quality on responding traffic.* The residual traffic `dns-recursive-01` is still serving has normal error and latency profiles. This is a quantity collapse, not a quality degradation.

**Key insight.** This is the failure mode an error-rate monitor misses entirely: `dns-recursive-01` didn't return bad answers, it returned almost no answers. Clients that normally hit it are either failing over to `dns-recursive-02` cleanly (most appear to be, based on the +85% pickup) or failing silently in ways the network sees nothing of. With `dns-recursive-02` now carrying 1.85× its baseline load, it has become a single point of failure for the active client base.

**What to do**

- Verify `dns-recursive-01` reachability (ping, SSH, console). Check for planned maintenance or recent change tickets.
- Monitor `dns-recursive-02` capacity — it's now serving 1.85× baseline traffic with no redundancy.

**Drill in further**

- Check the health of `dns-recursive-01` directly
- Show TCP connection counts on `dns-recursive-01` over the last 4 hours
```

---

## Continuation Prompt

For Warning/Degraded/Insufficient-Evidence reports in default mode, optionally end the turn by offering the top drill-downs as a follow-up choice. The report stays self-contained; the prompt is a separate turn-ender that reduces friction on the next step.

**Client capability.** If your client exposes an interactive prompt/choice primitive (tappable single-select options), use it — it's the lowest-friction form, especially on mobile. If it doesn't (most generic and MCP harnesses), present the same options as a short numbered plain-text list at the end of the turn. The content and rules below are identical either way; only the rendering differs.

### When to append

Append only when **all four** hold:

1. Verdict is Warning, Degraded, or Insufficient Evidence (skip Normal — user got their answer)
2. ≥ 2 chat-actionable drill-downs exist
3. Default mode is active
4. Interactive context (skip headless, scheduled, `/loop`, tagging)

### Options

- 1–2 options mirror the top "Drill in further" items as short tappable labels (≤ ~40 chars)
- 1 escape hatch — non-negotiable. "I'll take it from here", "Stop here", or similar
- Optional 1 wildcard ("Run a different check") when there's scope-pivot breadth
- 2–4 options total (interactive primitives often cap at 4)
- single-select almost always

Order: drill-downs first, wildcard if used, escape hatch last.

### Question phrasing

Short and orientational. Frames the choice, doesn't restate the finding.

- ✓ "Where would you like to investigate next?"
- ✓ "How would you like to continue?"
- ✗ "Now that we know `web-app-01` is degraded, where should we go?"

### Example

After the `web-app-01` device check (Example 1), end with a choice like this. If your client has an interactive single-select primitive, render these as options; otherwise list them as plain text:

- Question: "Where would you like to investigate next?"
- Options:
  - "Run a full health check on db-prod-02"
  - "Show slow DB transactions on db-prod-02"
  - "Check something else"
  - "I'll take it from here"

### Skip even within the rules

- Stale-data reports (the report is itself a refusal; a prompt is incongruous)
- Insufficient Evidence due to low activity (next step is "rerun with longer window" — already in bullets)
- Quick-look mode (intentionally minimal)

---

## NEW vs CHRONIC Verdict Modifier

The same verdict means very different things depending on prior history. A server that was Warning last week and is still Warning this week is performance debt, not an on-call event. A server that was Normal last week and is now Warning is a new problem.

After computing the current-window verdict, run the same assessment on the baseline window:

- Same as prior → **chronic**
- Worse than prior → **new**
- Better than prior → **recovered**

Omit when prior-period data is unavailable or below the activity gate. Apply in the verdict line under the title AND on individual findings bullets that earn one. For the overall status, use the modifier from the worst-affected category that drove the verdict.

---

## Bimodal Fleet Presentation

When a fleet check has a wide HSI spread, the average is operationally misleading. A fleet where 12 of 19 servers are at HSI 99% and 3 are at HSI 60% has a mean around 85% — reads as "uniformly mediocre" when the truth is "mostly excellent with 3 problems."

**Detection.** Bimodal when either:
- Per-device HSI standard deviation > 0.10, OR
- MAD > 0.05 AND at least one device > 2 MAD below the median.

**Reporting.** Lead the problem statement with the shape, not the average:

- ✓ "Most of the fleet is healthy, but 3 servers are newly degraded this week."
- ✗ "Fleet HSI: 84.9% (Fair) across 19 servers."

In the findings list, group chronic and new findings into separate categories rather than mixing under "HTTP latency." Use a synthetic category like *Performance debt* for chronic-high stable servers (see Example 2). The visual separation lets the reader see "what's new" vs "what's persistent" immediately.

When unimodal, the average is meaningful and can be stated directly.

---

## Stale Data Handling

When freshness check indicates data > 10 minutes old, the report IS the warning. Don't issue a verdict and bury staleness in confidence:

```markdown
## Health Check: <target>

**Insufficient Evidence** · Data stale

ExtraHop telemetry for this target is <X minutes> stale. A health verdict on stale data would be misleading — the agent is effectively blind for that window.

**What to do**

- Investigate sensor or appliance connectivity. Check ingestion pipelines.
- Verify the target device is still being observed (recent traffic on the relevant sensor).

**Drill in further**

- Rerun the health check once data freshness recovers
```

A Normal verdict on stale data is the worst possible output. This is the most important guardrail.

---

## Quick-look Mode

For "tldr" / "quick check" / "is everything okay" / "headline only":

```markdown
## Health Check: <target>

**<Verdict>** · <Time window>

<one-sentence problem statement, or "Healthy. All primary protocols within normal ranges.">

Ask me for the full report or to drill into a specific finding.
```

That's the whole output — no findings list, no insight, no next steps.

---

## Detailed Mode

For scheduled runs, audits, tagging, explicit-request, or programmatic consumers. Preserves the older verbose format.

### Format

```markdown
**Overall status: <STATUS>.** <one-sentence summary>
**User impact:** <who is affected, how badly, blast radius>
**Likely cause:** <downstream root cause if known, else "appears localized" or "unclear">

**Scope:** <environment | device: name (role) | protocol: name>
**Time range:** <window, ending HH:MM local TZ>
**Confidence:** <High | Medium | Low> — <one-line reason>. *<decision aid>*
**HSI:** <N>% (<Band>) — <bucket breakdown>

## Key Findings

<2–4 sentence analytical paragraph correlating findings.>

## What changed

| Category | Status | HSI | Current | Baseline | Delta | Pattern |
|---|---|---|---|---|---|---|

### <Category Name> — <STATUS>

<1–2 sentence explanation.>

- **HSI:** <N>% (<Band>) — <bucket breakdown>
- **Metric:** <current> (baseline: <baseline>, delta: <delta>)
- **Pattern:** <sustained | transient | intermittent | step-change at HH:MM>
- **Affected:** <devices, sensors, "fleet-wide">
- **Reclassification note:** <if applicable>

## What's steady

<one-line summary of Normal categories>

## Recommended next steps

**Drill deeper — paste back to continue:**
- → Ask: "<follow-up>"

**Take action — human operator:**
- → Do: <operator action>

<details>
<summary>Machine-readable summary</summary>

```yaml
scope: device
target: ...
overall_status: ...
hsi: 0.87
findings: ...
```
</details>
```

### When to use which mode

Precedence is top-down, first match wins (mirrors the "Mode selection" list in
`SKILL.md`). Artifact-oriented terms select HTML; content/structure terms select
Detailed; the word "report" **alone** is not an HTML trigger.

| Situation | Mode |
|---|---|
| Asks for "HTML," "PDF," "shareable," "deliverable," "one-pager," "export," "for leadership," or `--report` | HTML report (see `html-report.md`) |
| Asks for "the full report" / "detailed view" / "structured data" / "everything" | Detailed |
| Scheduled / cron / `/loop` | Detailed |
| Tagging mode | Detailed |
| Downstream agent consuming output | Detailed |
| "tldr" / "is everything okay" | Quick-look |
| Interactive chat, default health check request (incl. bare "report") | Default |
| Combines cues, e.g. "detailed PDF" | HTML report (artifact term wins) |
| Unclear whether a file or richer chat is wanted | Ask |

---

## HSI

Computed internally for every assessment meeting the activity gate. Two roles:

1. **Verdict calibration.** HSI < 0.50 → Degraded; 0.50–0.93 → Warning; ≥ 0.94 → Normal. Bounds the verdict against per-category threshold inconsistency.
2. **Trend tracking** across scheduled runs.

**Not displayed in default mode.** Appears in detailed mode and YAML footer.

### Methodology

Every response classified into one of three buckets:

- **Satisfied** — successful (no actionable error) AND latency ≤ T
- **Tolerating** — successful AND T < latency ≤ 4T
- **Frustrated** — actionable error of any kind, OR latency > 4T

```
HSI_category = (Satisfied + 0.5 × Tolerating) / Total
HSI_device = Σ(Satisfied_p + 0.5 × Tolerating_p) / Σ(Total_p) across primary categories p
HSI_fleet = same, across devices
```

Secondary categories (per role weighting in `domain-knowledge.md`) don't contribute to HSI_device.

### Per-category T (4T is fixed)

| Protocol | T | 4T |
|---|---|---|
| HTTP — application | 200ms | 800ms |
| HTTP — static / CDN | 50ms | 200ms |
| DNS — authoritative | 5ms | 20ms |
| DNS — recursive / forwarding | 50ms | 200ms |
| Database — OLTP | 100ms | 400ms |
| Database — OLAP | 5s | 20s |
| LDAP | 50ms | 200ms |
| Kerberos | 20ms | 80ms |
| SMB / CIFS (`access_time`) | 50ms | 200ms |

### Bands

| HSI | Band |
|---|---|
| ≥ 94% | Excellent |
| 85–93% | Good |
| 70–84% | Fair |
| 50–69% | Poor |
| < 50% | Unacceptable |

### Activity gate

HSI requires ≥ 100 samples in the assessment window for driving primary categories. Below this:

- Don't compute HSI.
- Default mode: category bullet says "Insufficient Evidence" with a one-line reason.
- Detailed mode: display bucket counts (`12 Satisfied / 0 Tolerating / 0 Frustrated (insufficient samples)`).

### Approximating from dataset metrics

`tprocess` is returned as a frequency distribution. To bucket without per-sample data:

- **Frustrated count** = actionable errors + count(tprocess > 4T), interpolated from percentile values bracketing 4T
- **Satisfied count** = count(tprocess ≤ T), interpolated from percentile values bracketing T
- **Tolerating count** = total − Satisfied − Frustrated

When `calc_type: "histogram"` is available (newer firmware), prefer that — interpolation is mildly conservative on long-tailed distributions and can under-count Frustrated on the worst-performing devices.

---

## Formatting Rules (default mode)

- Plain Markdown only — no box-drawing, fake column alignment, decorative emoji, or icons.
- H2 (`##`) for the report title. No H1. No H2 inside the report — use bold inline labels.
- Verdict-first bullets, italicized category, em-dash + period separator.
- Identifiers in backticks.
- Magnitudes in human units. `1.4s` not `1400ms`. `142 GB` not bytes. `2.3%` not `0.023`.
- Verdict casing: title case visible, uppercase in YAML.
- Time format: relative + local TZ. UTC anchor only in YAML.
- No metric names in body prose — use display names.
- No threshold quotes — state the value and the conclusion.
- Cap each next-steps section at 3–4 items.

---

## YAML Footer Schema (Detailed mode only)

```yaml
scope: <environment | device | protocol>
target: <string>
target_role: <string>
target_oids: [<int>]
sensors_observed: [<int>]
window: <duration string>
window_end_utc: <ISO timestamp>
overall_status: <NORMAL | WARNING | DEGRADED | INSUFFICIENT_EVIDENCE>
verdict_modifier: <new | chronic | recovered | null>
user_impact:
  affected_population: <string>
  affected_volume_estimate: <string>
  blast_radius: <string>
likely_root_cause:
  tier: <string>
  device: <string>
  evidence: <string>
hsi: <float 0..1>
hsi_band: <Excellent | Good | Fair | Poor | Unacceptable>
hsi_buckets: {satisfied: <int>, tolerating: <int>, frustrated: <int>, total: <int>}
confidence: <high | medium | low>
data_freshness_seconds: <int>
baseline: <string>
volume_drop_check:
  performed: <bool>      # always true; populated even on clean checks
  anomalies: [<string>]
findings:
  - category: <string>
    status: <string>
    verdict_modifier: <new | chronic | recovered | null>
    hsi: <float>
    pattern: <string>
    affected: [<string>]
    reclassification: <string when applicable>
fleet_distribution:
  bimodal: <bool>
  hsi_mean: <float>
  hsi_median: <float>
  hsi_min: <float>
  hsi_max: <float>
  outlier_count: <int>
recommended_followups: [<string>]
recommended_actions: [<string>]
caveats: [<string>]
```
