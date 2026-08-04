# Console URL Construction

Turn a Detection Set into a launchpad: link each detection, investigation, and
participant device to its exact page in the RevealX console so the analyst can
jump from the triage conclusion straight to the evidence in one click. The chat
session is the triage; the console is where the analyst takes it forward.

This mirrors the deep-link behavior in the companion `extrahop-health-check`
skill, including the same source tool (`extrahop_get_appliance_metadata`) and
the same hard rule: **never fabricate a URL.** A correct unlinked report is
strictly better than a confidently wrong link that sends an analyst to the
wrong tenant or a 404.

---

## When to construct URLs

Build a link whenever a Detection Set names a navigable target:

- **Detections** — link each detection ID (`#<id>`) in the `Detections:` line to
  its detection-detail page. This is the highest-value link: it lands the
  analyst on the exact card they are dispositioning.
- **Participants** — link an offender/victim **device** identifier to its device
  overview page (same pattern as the health-check skill). IP-only participants
  with no device OID are not linkable; leave them as plain text.
- **Investigations** — once `extrahop_create_investigation` returns an
  investigation ID, link that ID to the investigation page so the analyst can
  open the freshly created case.
- **Similar past detections** — link those IDs to their detection-detail pages
  too, since the analyst will likely want to compare.

Skip links in:

- **Batch close summaries** — the per-ID closing list can run to dozens or
  hundreds of IDs; linking every one is noise. Link only the **excluded** items
  (the ones pulled from the batch for individual handling) and, if useful, one
  representative detection. The bulk list stays plain.
- **Escalation queue blocks** — these are an internal worklist handed to L2 in
  the same session, not an operator-facing deliverable. Plain IDs are fine; L2
  can link them when it presents its own Detection Set.
- Any report where the FQDN is unknown (see below) — emit plain text.

---

## Prerequisites: FQDN and appliance UUID

Every console URL needs the console **FQDN**; device URLs additionally need an
**appliance UUID**. Detection and investigation URLs need only the FQDN.

- **Console FQDN** (e.g. `tenant.cloud.extrahop.com`) — the customer's
  RevealX hostname. Forms the URL base `https://<fqdn>/extrahop/#/`.
- **Appliance UUID** — a 32-character hex string identifying the appliance
  hosting the device data. Required only for device-participant URLs, as the
  `<appliance_uuid>.<discovery_id>` composite.

### Acquiring the FQDN and appliance UUID

`extrahop_get_appliance_metadata` returns both pieces. Its field names are
counter-intuitive, so read them carefully:

| Field | Holds | Use for |
|---|---|---|
| `display_host` | The console FQDN (e.g. `tenant.cloud.extrahop.com`) | **FQDN** — primary source |
| `external_hostname` | Usually the same FQDN | **FQDN** — fallback if `display_host` is empty |
| `hostname` | The 32-hex **appliance UUID** (NOT a hostname) | **Appliance UUID** |
| `mgmt_ipaddr` | Management IP | Never use for URLs |

1. **Call `extrahop_get_appliance_metadata`.** Read the FQDN from `display_host`
   (fall back to `external_hostname`) and the appliance UUID from `hostname`.
   This single call yields both. Cache them for the session.
2. **(Fallback) Parse a console URL the user already pasted** in this
   conversation, matching `https://<fqdn>/extrahop/#/...`. A pasted device URL
   of the form `/metrics/devices/<32hex>.<16hex>/` also yields the appliance
   UUID (the 32-hex prefix). Use this only if the tool is unavailable.
3. **Prior session memory**, if available and the user has used this skill
   before in the same environment.

4. **No FQDN -> no links.** If none of the above yields a hostname, **do not
   construct any links.** Present the Detection Set with plain `#<id>` and
   `name (device/<OID>)` text. Do not guess the hostname.

If you have the FQDN but not the appliance UUID, you can still build detection
and investigation links (they need only the FQDN) and skip the device-overview
links rather than fabricating the UUID. Don't derail a triage to chase the UUID.

### Caching

Acquire each piece **once per session**, then cache and reuse for every link in
every Detection Set. A new session re-acquires — that's fine.

### Never fabricate

- Never invent the FQDN. A plausible-looking domain (`acme.extrahop.com`) can
  send the analyst to an unrelated tenant or a 404, and in a shared-screen
  review a wrong FQDN can leak another customer's existence. No FQDN -> no links.
- Never invent the appliance UUID; the 32-hex value isn't guessable.
- Never confuse the `hostname` field (the appliance UUID) with the FQDN, and
  never substitute the management IP (`mgmt_ipaddr`) for the FQDN.

---

## URL syntax

### Detection detail page

```
https://<fqdn>/extrahop/#/detections/detail/<detection_id>
```

`detection_id` is the **full numeric API id** returned by
`extrahop_search_detections` or `extrahop_get_detection` — not the abbreviated
short id displayed in the RevealX console UI. Use the same full id as the
visible `#<id>` label in the Detection Set `Detections:` line.

Example (detection `412316861591`):

```
https://tenant.cloud.extrahop.com/extrahop/#/detections/detail/412316861591
```

### Investigation page

```
https://<fqdn>/extrahop/#/detections/investigations/<investigation_id>
```

Example (investigation `102`):

```
https://tenant.cloud.extrahop.com/extrahop/#/detections/investigations/102
```

### Device participant page (overview)

Reuses the device-URL pattern from the `extrahop-health-check` skill. The
composite device identifier is `<appliance_uuid>.<discovery_id>`:

```
https://<fqdn>/extrahop/#/metrics/devices/<appliance_uuid>.<discovery_id>/overview/
```

- `appliance_uuid` — 32 hex chars, environment-constant (see Prerequisites).
- `discovery_id` — 16 hex chars, returned by `extrahop_get_device` as
  `discovery_id` (or `extrahop_id`; both carry the same value).

A time window is optional on triage device links — unlike the health-check
skill, a detection already pins the analyst to the relevant moment. Omit the
`?from=...&interval_type=...&until=0` params unless you want to scope the device
page to the detection's window, in which case use the same time-parameter
mapping documented in the health-check `console-urls.md`.

---

## Formatting in the report

Wrap the identifier in a Markdown link, keeping the identifier readable. In the
Detection Set the detection ID and participant identifiers are the natural link
anchors.

- Detection ID: `[#412316861591](https://.../detections/detail/412316861591)`
- Participant device: `[web-prod-01](https://.../metrics/devices/<uuid>.<did>/overview/) (device/12345)`
- Investigation: `[#102](https://.../detections/investigations/102)`

Link the **first occurrence** of each identifier in a given Detection Set.
Repeat occurrences stay plain.

---

## Examples

These use FQDN `tenant.cloud.extrahop.com` and (for the device link)
appliance UUID `7946be2a04354967a2ff79788087ee24`, both from
`extrahop_get_appliance_metadata` (FQDN from `display_host`, UUID from
`hostname`).

### Detection IDs in a Detection Set

```markdown
- **Detections:** [#48213](https://tenant.cloud.extrahop.com/extrahop/#/detections/detail/48213) Network Scan, [#48217](https://tenant.cloud.extrahop.com/extrahop/#/detections/detail/48217) Network Scan
```

### Participant device

```markdown
  - Offender: [vuln-scanner-01](https://tenant.cloud.extrahop.com/extrahop/#/metrics/devices/7946be2a04354967a2ff79788087ee24.02bc5bb970bf0000/overview/) (device/90211)
```

### Newly created investigation

After `extrahop_create_investigation` returns id `102`:

```markdown
Investigation [#102](https://tenant.cloud.extrahop.com/extrahop/#/detections/investigations/102) created with detections #51002, #51010.
```

---

## Safeguards

- **Never fabricate.** No guessing the FQDN, appliance UUID, or discovery_id. No
  FQDN available -> emit the report unlinked. Better unlinked than wrong-linked.
  From `extrahop_get_appliance_metadata`: FQDN is `display_host`/`external_hostname`,
  appliance UUID is `hostname`, never `mgmt_ipaddr`.
- **Don't link the bulk batch-close list.** Linking dozens of IDs is noise; link
  only excluded items and a representative.
- **Don't substitute links for explanation.** Each Detection Set must read
  correctly on its own. An analyst skimming on a phone shouldn't need to tap a
  link to know the verdict.
- **Sensitive environments.** Links are harmless to recipients without console
  access and useful to those who have it, so it's safe to leave them in reports
  that may be pasted into a ticket — provided the FQDN was obtained, not guessed.
