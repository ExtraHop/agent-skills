# Escalation: Triage to Investigation Bridge

Connects L1 bulk triage to L2 deep investigation. Use it for the common
enterprise flow: triage a large queue, then deep-dive the small set worth it.

## Contents

- One session, two modes
- The escalation queue and handoff packet
- Where the queue lives (in-context vs. file)
- Prioritization
- Escalation grouping (one investigation vs. many)
- L1 proposes, L2 confirms
- Bulk-investigation guardrail
- Presentation

## One session, two modes

L1 Triage and L2 Investigation are **modes of a single Claude conversation**,
not separate agents or background processes. "Escalation" is an intra-session
hand-off: L1 produces a worklist, then Claude switches to L2 (by following
[investigation-workflow.md](investigation-workflow.md)) and works that list.
Do not wait on another agent — there is none.

## The escalation queue and handoff packet

When L1 finishes triage, everything not closed and worth deeper analysis goes
into the **escalation queue**. Each entry bundles the worklist item with the
evidence L1 already gathered (the **handoff packet**), so L2 starts from context
instead of re-fetching. One combined structure per item or group:

- `detection_ids` — the item, or the group that will become one investigation.
- `escalation_reason` — why it left triage (malicious true positive, or
  undetermined-but-suspicious).
- `priority` — `High` / `Medium` / `Low` from the rule below.
- `preliminary_verdict` + `confidence`.
- `participants` — already resolved: device OID **and** `discovery_id`,
  criticality, role. L2 reuses these for record pivots without re-calling
  `extrahop_get_device`.
- `attack_techniques` — MITRE ATT&CK techniques from
  `extrahop_get_detectiontypemetadata`.
- `evidence_snapshot` — key facts L1 already pulled (risk scores, timeline
  highlights).
- `open_questions` — what L2 must resolve to confirm or dismiss.
- `proposed_investigation_grouping` — which IDs belong in one investigation.

## Where the queue lives (in-context vs. file)

**Default: in-context.** Emit the queue as a Markdown block (see Presentation).
L2 re-reads it from conversation history. This works in every client and
leaves nothing to clean up.

**Upgrade to a file** only when both hold:

- the environment has a writable filesystem (for example Claude Code), and
- the queue is large enough that context loss is a real risk — a judgment call
  based on item count and how long the session has run.

When upgrading, write the queue as JSON to `escalation-queue.json` in the
working directory and tell the user the path. L2 reads it back from there. As
L2 dispositions each entry, mark it resolved in place in the file. When every
entry is resolved, offer to delete the file so no stale worklist lingers.

Do not assume a filesystem exists; the in-context queue is always the fallback.

## Prioritization

Order the queue so L2 works the highest-impact items first. `search_detections`
won't sort for you, so compute priority **client-side** over the population L1
already pulled. Weigh:

- **Risk score** — higher detection risk ranks higher.
- **Critical participants** — `is_critical` offenders or victims raise priority.
- **Correlation** — items spanning multiple detections or adjacent attack
  stages outrank isolated singletons.
- **Recency** — active or most-recent activity outranks stale.

Assign `High` / `Medium` / `Low` and sort the queue by it.

## Escalation grouping (one investigation vs. many)

Decide investigation boundaries before L2 opens cases. Group escalated
detections into **one** investigation when they share:

- a participant (same offender or victim), or
- an adjacent attack stage (recon -> exploitation -> lateral movement ->
  exfiltration) on the same assets, or
- an overlapping time window consistent with one campaign.

Unrelated malicious true positives stay separate — one investigation each.
Mis-grouping fragments incident response, so favor a single coherent case when
the evidence ties detections to one attack chain.

## L1 proposes, L2 confirms

L2 is what confirms a malicious true positive. Therefore:

- **L1 may open an investigation directly only for a clear-cut, High-confidence
  malicious true positive** — judgment-based.
- **Medium-confidence or uncertain** malicious true positives, and all
  undetermined-but-suspicious items, are **escalated to L2 first**. L2 confirms,
  then decides whether to open the investigation.

This keeps weak evidence from spawning low-value investigation cases.

## Bulk-investigation guardrail

Deep investigation is expensive (records pulls, pcaps). When the queue is large,
do **not** auto-deep-dive everything. L2 investigates the prioritized items by
judgment and summarizes the remainder as the still-open queue, so the session
stays focused and the rest of the worklist is visible for follow-up.

## Presentation

Emit the escalation queue as a Markdown block at the end of L1:

```markdown
### Escalation Queue (4 items)

1. **[High]** #51002 Suspicious SMB Access, #51010 Kerberos Ticket Anomaly
   - Reason: malicious true positive (Medium confidence) — confirm in L2
   - Participants: jump-01 (device/77140, discovery_id 5254..ab, critical),
     fileserver-03 (device/77320, discovery_id 5254..cd)
   - ATT&CK: T1021.002, T1558
   - Proposed investigation: group both (shared offender, adjacent stages)
   - Open questions: confirm credential use; check for staged data

2. **[Medium]** #50880 Unusual DNS Volume
   - Reason: undetermined-but-suspicious — needs record correlation in L2
   - Participants: host-22 (device/61003, discovery_id 5254..ef)
   - ATT&CK: T1071.004
   - Proposed investigation: standalone
   - Open questions: is this beaconing or a misconfigured client?
```

L2 consumes this list top-down. See
[investigation-workflow.md](investigation-workflow.md) Step 0.
