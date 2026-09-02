# Detection Set Output Format

A Detection Set is one verdict over a group of related detections, plus a
recommended action. In the original app this rendered as an interactive card;
here it is a Markdown block. Present one Detection Set per group.

## Template

```markdown
### Detection Set: <title>

<one- or two-sentence synopsis of what these detections represent>

- **Verdict:** <False Positive | Benign True Positive | Malicious True Positive>
- **Confidence:** <Low | Medium | High>
- **AI disposition:** <false_positive | benign_true_positive | malicious_true_positive | indeterminate>
- **Recommended action:** <Close | Create Investigation>
- **Detections:** #<id> <type>, #<id> <type>, ...  <!-- id = full numeric API id from extrahop_search_detections/extrahop_get_detection, never the abbreviated console id -->
- **Participants:**
  - Offender: <name or IP> (device/<OID> or ipaddr)
  - Victim: <name or IP> (device/<OID> or ipaddr)
- **Human outcome:** <only if a person already dispositioned/closed this — name the human resolution or investigation assessment, and flag if it disagrees with the AI disposition; omit otherwise>
- **Similar past detections:** #<id>, ... (omit if none)

**If Close:**
- Resolution: <no_action_taken | action_taken>
- Notes: <why this is a false positive or benign; if action_taken, name the action that was performed>

**If Create Investigation:**
- Suggested name: <concise investigation name>
- Risk / focus: <risk assessment and what to investigate first>
- Blast radius notes: <affected assets and scope for the investigation notes>
```

Render entity references as plain text with the identifier in parentheses, for
example `web-prod-01 (device/12345)` or `10.4.0.7 (ipaddr)`. There are no
clickable pills in a text interface.

Keep `Detections:` as a **single inline comma-separated list on the one
bullet** — `- **Detections:** #123 Foo, #124 Bar`. Do **not** break the
detections onto nested sub-bullets:

```markdown
<!-- WRONG — renders an empty detections row and yields zero closable IDs -->
- **Detections:**
  - #123 Foo
  - #124 Bar
```

The app parses the inline form to populate the card and to build the close /
create-investigation calls; a sub-bullet layout produces zero detections.
`Participants:` is the one block where sub-bullets are expected (one per
`Offender:`/`Victim:` line) — `Detections:` is not.

Always use the **full numeric API id** (the `id` field from
`extrahop_search_detections` or `extrahop_get_detection`) as the `#<id>` token
in the `Detections:` line and in `Similar past detections`. Never abbreviate it
to the short console display id — the app uses this value to call the API
directly when the analyst clicks Close or Create Investigation.

When the console FQDN is available, wrap the natural link anchors in Markdown
links to the RevealX console (detection IDs -> detection-detail page,
created investigation IDs ->
investigation page). The full id stays in the visible label — adding a link
never abbreviates it, e.g.
`[#4294975901](https://.../detections/detail/4294975901) DCSync Activity`.
Link the first occurrence of each identifier per Detection Set. If no FQDN is
available, leave identifiers as plain text — never fabricate a URL. Do not link
the bulk batch-close ID list (link only excluded items). Full syntax and
guardrails in [console-urls.md](console-urls.md).

Omit fields that do not apply (for example participants when unknown, or the
Close/Create Investigation block that is not selected). Keep the synopsis and
notes factual and grounded in tool results.

`ai_disposition` is the AI verdict, recorded on detections you **close or
escalate** (and on a Low-confidence item you deliberately leave open as your
verdict) — it is the signal scored against human ground truth to measure AI
accuracy. Recording it on transient noise you never act on is optional. Never
overwrite a disposition a human already set; if a human outcome already exists,
show it on the **Human outcome** line and flag any disagreement instead of
clobbering it. `resolution` reflects whether a response actually occurred —
default `no_action_taken`; use `action_taken` only when the session shows a real
action was performed, and name it in the notes. See the batch close decision
tree in [triage-workflow.md](triage-workflow.md).

## Example — Close

```markdown
### Detection Set: Internal vulnerability scanner activity

Three "Network Scan" detections all originate from the authorized security
scanner during its scheduled window. Behavior matches expected scanning.

- **Verdict:** Benign True Positive
- **Confidence:** High
- **AI disposition:** benign_true_positive
- **Recommended action:** Close
- **Detections:** #4294948213 Network Scan, #4294948217 Network Scan, #4294948230 Port Scan
- **Participants:**
  - Offender: vuln-scanner-01 (device/90211)

**If Close:**
- Resolution: no_action_taken
- Notes: Source is the authorized Qualys scanner running its nightly sweep.
  Targets and timing match the sanctioned scan policy.
```

## Example — Create Investigation

```markdown
### Detection Set: Possible lateral movement from jump host

Correlated SMB and Kerberos detections show jump-01 authenticating to multiple
servers it does not normally contact, shortly after a suspicious login.

- **Verdict:** Malicious True Positive
- **Confidence:** Medium
- **AI disposition:** malicious_true_positive
- **Recommended action:** Create Investigation
- **Detections:** #4294951002 Suspicious SMB Access, #4294951010 Kerberos Ticket Anomaly
- **Participants:**
  - Offender: jump-01 (device/77140)
  - Victim: fileserver-03 (device/77320)

**If Create Investigation:**
- Suggested name: Lateral movement from jump-01 (2026-06-01)
- Risk / focus: jump-01 contacted 6 new internal servers in 12 minutes; confirm
  credential use and check for staged data.
- Blast radius notes: Offender jump-01; servers touched include fileserver-03;
  review for further spread to the finance segment.
```

## Batch close summary

When closing a homogeneous set of false positives or benign true positives,
present one summary for the user to approve once before any close call. Keep
the per-ID list explicit so the user sees exactly what will close.

```markdown
### Close Batch: DNS lookups to internal resolver (false positive)

5 "Suspicious DNS Activity" detections, all from clients querying the
sanctioned internal resolver. Same detection type; benign explanation is
consistent across all.

- **Verdict:** False Positive — **Confidence:** High
- **AI disposition:** false_positive
- **Resolution:** no_action_taken
- **Homogeneity:** same detection_type (Suspicious DNS Activity); shared victim
  dns-resolver-01 (device/40012)
- **Closing (5):** #4294961001, #4294961002, #4294961003, #4294961004, #4294961005
- **Excluded (1):** #4294961050 — same type but victim is a critical domain
  controller dc-01 (device/40500); handling individually.
```

On approval, iterate `extrahop_update_detection` per ID in the closing list.

The `Closing (N):` line must **enumerate every full numeric API id inline**, and
the count `(N)` must equal the number of IDs listed. Do **not** abbreviate the
list with a range (`#…001 through #…042`), an ellipsis (`...`), or by offloading
it to a file — the app closes **exactly the IDs it parses from this line**, so
anything not listed is silently dropped from the approved action. If the batch
is genuinely large, list all the IDs anyway (there is no length cap); the count
exists to cross-check the enumeration, not to replace it.

Keep the bulk `Closing (N)` ID list as plain text — linking dozens or hundreds
of IDs is noise. Link only the **excluded** items (and optionally one
representative), since those are the ones the analyst will open and handle
individually. See [console-urls.md](console-urls.md).

## Escalation queue

True positives and undetermined-but-suspicious detections are not acted on in
triage — they are escalated to L2 as an **escalation queue** block, parallel to
the Close Batch. Each entry carries the worklist item plus the L1 evidence
(participants with OIDs/`discovery_id`s, ATT&CK techniques, priority, proposed
investigation grouping, open questions). For the structure, an example, and the
persistence rules, see [escalation.md](escalation.md).

## After approval

Present the Detection Set or batch summary, then wait for explicit user
approval before any state change:

- **Close (single)** -> `extrahop_update_detection` with `status="closed"`,
  `ai_disposition` set to the verdict, the chosen `resolution`, and notes.
- **Close (batch)** -> iterate `extrahop_update_detection` per detection ID,
  each with `status="closed"`, `resolution="no_action_taken"`, and
  `ai_disposition` set to the verdict.
- **Classify only (leave open)** -> `extrahop_update_detection` with
  `ai_disposition` set to the verdict and no status change. Non-destructive
  telemetry — no separate approval needed.
- **Create Investigation** -> `extrahop_create_investigation` with the
  detection IDs (`event_ids`), `name`, and `notes`.
