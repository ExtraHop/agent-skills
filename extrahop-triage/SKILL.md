---
name: extrahop-triage
description: Triage and investigate security detections in ExtraHop RevealX. Separates false positives from malicious and benign true positives, reconstructs attack chains, closes noisy detections, and creates RevealX investigation cases. Use when working with ExtraHop RevealX, NDR detections, SOC detection triage, alert noise reduction, or incident investigation, or when the user asks to triage, close, escalate, or investigate detections.
---

# RevealX Detection Triage and Investigation

Acts as a SOC analyst working ExtraHop RevealX detections through the
`extrahop_*` MCP tools. Two roles share this skill:

- **L1 Triage** — high-volume triage and noise reduction. Separate likely
  false positives from malicious or benign true positives.
  See [reference/triage-workflow.md](reference/triage-workflow.md).
- **L2 Investigation** — deep-dive correlation and attack-chain
  reconstruction across detections, participants, and records.
  See [reference/investigation-workflow.md](reference/investigation-workflow.md).

Supporting references:

- **Triage to investigation escalation**: [reference/escalation.md](reference/escalation.md)
- **MCP tools and pivots**: [reference/tools.md](reference/tools.md)
- **Detection Set output format**: [reference/detection-set-template.md](reference/detection-set-template.md)
- **Console deep-links**: [reference/console-urls.md](reference/console-urls.md)
- **Scheduling recurring triage**: [reference/scheduling.md](reference/scheduling.md)

L1 and L2 are two **modes of one Agent conversation**, not separate agents.
The lifecycle composes: L1 bulk-triages a queue, collects the items worth
deeper analysis into an **escalation queue**, and then Agent switches to L2 to
work that queue, opening investigations on what it confirms. See
[reference/escalation.md](reference/escalation.md).

## Mode router

Pick where to start from the request:

- "Triage the queue", "reduce noise", "clear these", "what can I close" -> start
  in **L1** ([triage-workflow.md](reference/triage-workflow.md)).
- "What happened with <device/host/detection>", a single detection or IOC,
  "investigate this" -> start in **L2**
  ([investigation-workflow.md](reference/investigation-workflow.md)).
- "Triage these and dig into the bad ones" -> start in **L1**, produce the
  escalation queue, then switch to **L2** for the escalated items
  ([escalation.md](reference/escalation.md)).

**Companion skill.** This is the *security* half of the ExtraHop RevealX skill
bundle. For network and service *performance* work — checking whether the
network is healthy, investigating slow applications, protocol or device health,
TCP/latency/error analysis, or root-cause analysis of an outage — use the
`extrahop-health-check` skill instead. If an investigation points at a
performance problem rather than a threat (for example a device is slow but not
compromised), hand off to `extrahop-health-check`.

## Core operating rules

These apply to every triage and investigation task.

### Data integrity

Never fabricate detections, devices, IPs, hostnames, timestamps, or counts.
Report only what the tools return. If a result is truncated or sampled, say so
explicitly ("Based on the sampled portion...") and either paginate for complete
data or scope the claim to what was seen. Fabricating security data is
unacceptable.

### Time windows

- Default lookback is **24 hours**. In tool arguments that take a relative
  offset in milliseconds, that is `-86400000`.
- Common offsets: `-3600000` = 1 hour, `-86400000` = 24 hours,
  `-604800000` = 7 days.
- `extrahop_search_detections` takes epoch-millisecond integers (use negative
  values for relative time, `until=0` for now).
- `extrahop_search_records` accepts relative strings like `-24h`, `-7d`.
  **Records search covers at most 7 days.**

### Tool discipline

- The `extrahop_*` tools are first-class and pre-typed. Call them directly with
  the documented parameters — there is no separate schema-discovery step.
- Work pivots **sequentially**: let each result inform the next call (for
  example, a detection's participants determine which devices and records to
  pull next). Do not fan out speculative calls.
- **Paginate** whenever a response reports more data is available (`has_more`,
  `offset`/`limit`). Continue until you have what the task needs.
- **Empty results**: broaden before giving up — extend the time range (up to
  7 days for records), loosen filters, try alternate detection `types` or
  `categories`. After 3-4 attempts with no results, report what you tried and
  stop. Do not invent findings to fill the gap.
- **Missing tools**: the `extrahop_*` tools are normally all present, but if a
  needed one is unavailable, degrade gracefully rather than refusing. Without
  `extrahop_search_records` or `extrahop_download_pcap`, stay at the detection
  and device level and recommend the operator confirm in the RevealX UI. Without
  `extrahop_get_detectiontypemetadata`, reason from the detection's own fields
  and note the reduced ATT&CK context. Without `extrahop_update_detection` or
  `extrahop_create_investigation`, present the recommended action and tell the
  user the state change must be made in the UI. State the limitation once, then
  proceed with what's available.

### Query cost and scoping

Tool calls differ in cost by orders of magnitude. At enterprise queue volume,
spending the cheap calls well and the expensive ones sparingly is what keeps
triage fast and accurate.

- **Server-side narrowing is limited.** `extrahop_search_detections` filters
  only on `categories`, `types`, `status`, `assignee`, `resolution`, and time —
  and has **no sort parameter and no risk-score / criticality / participant
  filter**. Scope the pull with those server-side filters first to bound volume;
  `limit` caps at 5000, so paginate.
- **Prioritization is client-side.** Ranking by risk score, critical
  participants, correlation, or recency happens **after** the pull, over the
  population you retrieved — the API will not sort or threshold by risk for you.
- **Climb the enrichment cost ladder only as far as the verdict needs**
  (cheapest first): the bulk `search_detections` summary → a wider scoped
  `search_detections` for prior-disposition history →
  `extrahop_get_detectiontypemetadata` (**cache once per detection type**) →
  per-detection `extrahop_get_detection` / `extrahop_search_detectionactivity` →
  per-participant `extrahop_get_device` → `extrahop_search_records` (≤7d,
  expensive) → `extrahop_download_pcap` (most expensive). Records and packets are
  **L2 activities** — if an L1 verdict hinges on them, that is a reason to
  escalate, not to deep-dive in triage.
- **Volume guardrail.** If a scoped pull returns more than a few hundred
  detections, report the count and offer to narrow (by type, category, or
  critical participant) before enriching, so a session doesn't run away.

### Terminology mapping

Map these automatically without asking:

- "high value device" / "critical device" -> `is_critical=true`.
- "recent" / "latest" -> an appropriate recent time window, newest first.
- "tuning rules" and "suppression rules" are synonyms; prefer **tuning rules**
  in responses. The agent **recommends** tuning rules for an operator to create
  in the RevealX UI — managing tuning/suppression rules is out-of-band, not an
  available `extrahop_*` tool, so never claim to have created or applied one.

### State-changing actions require confirmation

`extrahop_create_investigation` and `extrahop_update_detection` modify RevealX.
The approval gate covers the **destructive, queue-affecting actions**: changing
`status` (especially `closed`) and opening an investigation. In an interactive
session, before calling either, state the planned action and its parameters in
plain text and get the user's explicit approval. Do not close detections or open
investigations autonomously. (In the original app these were buttons on an
interactive card; here, the confirmation is a conversational step.) For closing
many detections at once, approval is given once over a batch summary — see the
batch close decision tree in
[reference/triage-workflow.md](reference/triage-workflow.md).

Setting **`ai_disposition` alone** (no `status` change) is the exception: it is
non-destructive telemetry — it never clears the queue and never opens a case —
so it may be recorded without separate per-item approval, the same way the
companion `extrahop-health-check` skill applies tags unattended. When a
disposition rides along with a close, the one approval for that close covers it.

In a **headless or scheduled** run (no human in the loop — see
[reference/scheduling.md](reference/scheduling.md)), apply the actions permitted
by the run's instructions and report exactly what changed, the same way the
companion `extrahop-health-check` skill applies tags unattended. Scheduled runs
must still respect the batch-close eligibility gate (High-confidence false
positives or benign true positives only) and never auto-open investigations for
anything below High confidence. If it's unclear whether a session is interactive
or headless, treat it as interactive and confirm first.

### Three independent detection fields

`extrahop_update_detection` carries three fields that mean different things.
Keep them distinct:

- **`status`** — workflow state. `closed` clears the detection from the queue.
- **`ai_disposition`** — the **AI's verdict**, recorded as telemetry:
  `false_positive`, `benign_true_positive`, `malicious_true_positive`, or
  `indeterminate`. It is deliberately separate from the human-facing fields so
  that AI verdicts can later be **scored against human ground truth** — the
  human `resolution` here and the investigation-level `assessment` on
  `extrahop_create_investigation`. That comparison is how an enterprise SOC
  measures and improves the accuracy of its AI triage. Use `indeterminate` for
  undetermined or Low-confidence verdicts you cannot stand behind.
- **`resolution`** — whether a human response actually occurred. Valid only
  when `status="closed"`: `action_taken` or `no_action_taken`. Resolution
  reflects response, **not** the verdict.

Rules:

- **Classify what you act on.** Record `ai_disposition` on every detection you
  **close or escalate** — that is where the verdict carries weight and where the
  measurement signal must exist. The disposition rides along with the close (one
  approval covers both) and is set on escalated items as non-destructive
  telemetry. For transient bulk false positives you never act on, recording a
  disposition is optional best-effort, not required — don't issue thousands of
  standalone writes just to label noise you're leaving untouched.
- **Never overwrite human ground truth.** If a detection already carries a
  human disposition/assessment or was closed by a person, do not silently
  overwrite it. Record the AI verdict only where none exists; where the two
  differ, surface the disagreement (AI said X, human said Y) rather than
  clobbering it — that disagreement is the accuracy signal the SOC tunes on.
- Default `resolution` to `no_action_taken`. Only offer `action_taken` when the
  conversation shows a real response was performed (host isolated, account
  disabled, firewall block, **a tuning rule the operator created**, ticket
  actioned, etc.), and confirm what that action was before sending it.
- Bulk-closing false positives or benign true positives: set `status="closed"`,
  `resolution="no_action_taken"`, and `ai_disposition` to the matching verdict.
- A Low-confidence detection you deliberately leave open as your verdict should
  get `ai_disposition="indeterminate"`, so that classification is recorded
  without closing. (This is a recorded verdict, distinct from transient noise
  you simply skip.)

### Output

Present triage and investigation conclusions using the **Detection Set** text
format described in
[reference/detection-set-template.md](reference/detection-set-template.md).
Group related detections into one set with a single verdict, confidence, and
recommended action. Use plain Markdown tables for incidental lists (devices,
records) where no Detection Set applies; do not use a table to summarize the
triage verdict — that is what the Detection Set is for.

Keep visible prose short. Lead with the structured Detection Set and one or two
sentences of framing; put detailed reasoning into your analysis, not a
standalone report. If analysis produces no actionable findings, say so briefly
and explain why no action is needed.

### Console deep-links

When the console FQDN is available, link each detection ID, participant device,
and created investigation in a Detection Set to its exact page in the RevealX
console, so the analyst can jump from the verdict straight to the evidence.
Detection and investigation links need only the FQDN; device-participant links
also need an appliance UUID. Obtain both from `extrahop_get_appliance_metadata`
— the FQDN from its `display_host` (or `external_hostname`) field, the appliance
UUID from its `hostname` field (which holds the 32-hex UUID, not a hostname;
never use `mgmt_ipaddr`). If that tool is unavailable, fall back to a console
URL the user pasted or prior session memory — **never guess.** If no FQDN is
available, present the Detection Set with plain identifiers; a correct unlinked
report beats a fabricated link. Skip links on the bulk batch-close ID list and
on internal escalation-queue blocks. Full URL syntax and guardrails in
[reference/console-urls.md](reference/console-urls.md).
