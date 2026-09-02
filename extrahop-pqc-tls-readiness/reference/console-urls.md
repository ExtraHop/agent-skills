# Console deep-links

Let the reader jump from a report row to the device group's TLS page at the same window the
report used. The report is the assessment; the console is where they verify it.

**Never fabricate a URL.** A correct unlinked report is strictly better than a confidently
wrong link that sends the reader to the wrong tenant or a 404.

---

## Prerequisite: console FQDN

`get_appliance_metadata` returns the console FQDN:

| Field | Actually holds | Use for |
|---|---|---|
| `display_host` | The console FQDN | **FQDN** — primary |
| `external_hostname` | Usually the same FQDN | **FQDN** — fallback |
| `mgmt_ipaddr` | Management IP | **Never** use for URLs |

**Fallback:** parse a console URL the user already pasted, matching
`https://<fqdn>/extrahop/#/…`.

**No FQDN → no links.** Emit plain identifiers. Do not guess a hostname: a plausible
domain can point at an unrelated tenant, and on a shared screen a wrong FQDN leaks another
customer's existence.

Cache the FQDN **once per session**.

---

## Syntax

```
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

- ✓ `` [`TLS Server Activity`](https://…) ``
- ✗ `` `[TLS Server Activity](https://…)` `` — renders as literal text
- ✗ `[TLS Server Activity](https://…)` — loses identifier typography

Link the **first occurrence only**.

---

## Safeguards

- **One window per report** — every URL uses the assessment's window.
- **Don't substitute links for explanation.** The report must read correctly on its own; a
  reader skimming on a phone shouldn't have to tap through to learn which servers declined
  PQC.
- Links are harmless to recipients without console access and useful to those who have it,
  so they are safe in an exported PDF or a ticket — **provided the FQDN was obtained, not
  guessed.**
