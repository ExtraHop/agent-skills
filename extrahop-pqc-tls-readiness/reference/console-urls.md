# Console deep-links

Let the reader jump from a report row to the device's TLS page at the same window the
report used. The report is the assessment; the console is where they verify it.

**Never fabricate a URL.** A correct unlinked report is strictly better than a confidently
wrong link that sends the reader to the wrong tenant or a 404.

---

## The two prerequisites

`get_appliance_metadata` returns both in one call. **Its field names are
counter-intuitive** — read carefully:

| Field | Actually holds | Use for |
|---|---|---|
| `display_host` | The console FQDN | **FQDN** — primary |
| `external_hostname` | Usually the same FQDN | **FQDN** — fallback |
| `hostname` | The 32-hex **appliance UUID**, *not* a hostname | **Appliance UUID** |
| `mgmt_ipaddr` | Management IP | **Never** use for URLs |

Verified live: `display_host` = `console.example.com`, `hostname` =
`40ae3db4340c4748a9348d4c60528147`.

**Fallback:** parse a console URL the user already pasted, matching
`https://<fqdn>/extrahop/#/…`. A pasted device URL of the form
`/metrics/devices/<32hex>.<16hex>/` also yields the appliance UUID.

**No FQDN → no links.** Emit plain identifiers. Do not guess a hostname: a plausible
domain can point at an unrelated tenant, and on a shared screen a wrong FQDN leaks another
customer's existence.

With the FQDN but no UUID, device-group links still work (they need only the FQDN) — build
those and skip device links. Don't derail the inventory chasing the UUID.

Cache both **once per session**.

---

## Syntax

The composite device identifier is `<appliance_uuid>.<discovery_id>`:

- `appliance_uuid` — 32 hex, environment-constant.
- `discovery_id` — 16 hex, from `get_device` as `discovery_id` or `extrahop_id` (same
  value). **The OIDs from device enumeration are not the discovery_id.**

> **Do not pay for this twice.** The scoping pass (`scoping.md`) already calls
> `get_device` for any device it must disambiguate — **cache `discovery_id` from that same
> response.** A per-row `get_device` purely for links is a second O(N) cost for nothing.
> Devices you never fetched simply render unlinked.

```
# device, TLS server page
https://<fqdn>/extrahop/#/metrics/devices/<appliance_uuid>.<discovery_id>/ssl-server?from=30&interval_type=DAY&until=0

# device, TLS client page (Step 8)
.../ssl-client?from=30&interval_type=DAY&until=0

# device, SSH server page (Step 7)
.../ssh-server?from=30&interval_type=DAY&until=0

# device group (no appliance UUID needed)
https://<fqdn>/extrahop/#/metrics/devicegroups/<group_id>/ssl-server?from=30&interval_type=DAY&until=0
```

`group_id` is the integer from `search_devicegroups` — `54` for "TLS Server Activity",
`53` for "TLS Client Activity" on the verified console.

### Window parameters

Match the URL window to the report window:

| Report window | `from` | `interval_type` |
|---|---|---|
| Last 24 hours | `1` | `DAY` |
| Last 7 days | `1` | `WK` |
| **Last 30 days (default)** | `30` | `DAY` |

For a custom fixed window use absolute epoch **seconds** (10-digit,
`?from=<start>&until=<end>`, no `interval_type`). **The console uses seconds; metric
queries use milliseconds** — divide by 1000.

---

## Formatting

Wrap the backticked identifier; the backticks stay.

- ✓ `` [`web-app-01`](https://…) ``
- ✗ `` `[web-app-01](https://…)` `` — renders as literal text
- ✗ `[web-app-01](https://…)` — loses identifier typography

Link the **first occurrence only**. Same pattern for group names.

**Never link inside the CSV.** If the user explicitly wants clickable CSV output, add a
dedicated `console_url` column holding the bare URL — embedding `[…](…)` in another column
breaks CSV parsing.

---

## Safeguards

- **One window per report** — every URL uses the assessment's window.
- **Don't substitute links for explanation.** The report must read correctly on its own; a
  reader skimming on a phone shouldn't have to tap through to learn which servers declined
  PQC.
- **Skip unlinkable rows silently** — no `discovery_id`, no link, plain text, no apology.
- Links are harmless to recipients without console access and useful to those who have it,
  so they are safe in an exported PDF or a ticket — **provided the FQDN was obtained, not
  guessed.**
