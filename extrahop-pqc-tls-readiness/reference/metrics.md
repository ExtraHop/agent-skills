# Metric reference — stats, shapes, and the ways they lie

Stat names and dimensions verified against the live metric catalog and live queries on
firmware **26.3**. Where a claim was proven by a specific live response, the numbers are
given — treat them as illustrations of the mechanism, not as constants.

**Contents:** stats (TLS device/application, SSH) · reading values and the nested
`topn_tset` · the `cycle` trap · truncation surfaces · multi-sensor responses · driving the
console REST API directly.

---

## Stats

### TLS, device level

| Category | Stat | Dimension | Measures |
|---|---|---|---|
| `ssl_server` | `connected` | scalar | Sessions terminated by this server |
| `ssl_server` | `post_quantum_kex` | scalar | Sessions using a PQC key agreement |
| `ssl_server` | `key_agreement` | topn / string | Sessions by named group (PQC + classical) |
| `ssl_server` | `version` | topn / string | Sessions by TLS version |
| `ssl_server` | `cipher` | topn / string | Sessions by cipher suite — **not** key agreement |
| `ssl_server` | `weak_ciphers` | scalar | Sessions using a weak suite |
| `ssl_server` | `cert_pubkey_curve` | topn / string | Certificate public-key curve |
| `ssl_server_detail` | `key_agreement` | **topn_tset** string × ipaddr | Group × client IP |
| `ssl_server_detail` | `connected` | topn / ipaddr | Sessions per client IP |
| `ssl_server_detail` | `post_quantum_kex` | topn / ipaddr | PQC sessions per client IP |
| `ssl_server_detail` | `cert_pubkey_curve` | **topn_tset** string × ipaddr | Curve × client IP |

Every `ssl_server*` row above has an `ssl_client*` twin, where `_detail` keys are the
**server** IP rather than the client. `post_quantum_kex` exists as a scalar on
`ssl_client` too.

**Device-level protocol categories require the `_server` / `_client` suffix.** Bare `ssl`
works only for `application` and `capture` objects.

### TLS, application level

Only on `application` objects, and useful for service-oriented reporting:

| Category | Stat | Dimension |
|---|---|---|
| `ssl` | `post_quantum_kex` | scalar |
| `ssl_sni_detail` | `post_quantum_kex` | topn / string (SNI) |
| `ssl_certificate_detail` | `post_quantum_kex` | topn / string (cert subject) |
| `ssl_server_addr_detail` / `ssl_client_addr_detail` | `post_quantum_kex` | topn / ipaddr |

`ssl_sni_detail` is the closest thing to "PQC adoption per service name" the product
offers. It needs an Application object to exist, so it is opportunistic, not the default
path.

### SSH

| Category | Stat | Dimension | Measures |
|---|---|---|---|
| `ssh_server` / `ssh_client` | `sessions` | scalar | **The session denominator — not `connected`** |
| `ssh_server` / `ssh_client` | `kex_algorithm` | topn / string | Sessions by KEX algorithm |
| `ssh_server` / `ssh_client` | `cipher` / `server_cipher` | topn / string | Client- / server-side cipher |
| `ssh_server` / `ssh_client` | `mac` / `server_mac` | topn / string | MAC algorithm |
| `ssh_server` / `ssh_client` | `version` / `server_version` | topn / string | Client / server version banner |
| `ssh_server` / `ssh_client` | `implementation` / `server_implementation` | topn / string | Client / server implementation |
| `ssh_server` / `ssh_client` | `auth_successes`, `auth_failures` | scalar | Authentication outcomes |
| `ssh_server_detail` / `ssh_client_detail` | `kex_algorithm` | **topn_tset** string × ipaddr | Algorithm × peer IP |

> **The SSH denominator is `sessions`; the TLS denominator is `connected`. They are not
> interchangeable.** `ssh_server:connected` does not exist and the query fails with a bare
> **`400 Bad Request` naming no field**, so the mistake reads as a broken query rather than
> a wrong stat name. Confirm against `search_metric_catalog(metric_category = "ssh_server",
> object_type = "device")` rather than assuming the TLS shape carries over.

**There is no `post_quantum_kex` for SSH** — verified by catalog search: the only
`post_quantum_kex` stats are the `ssl*` ones above. SSH PQC must be classified by
algorithm name (`classification.md`).

---

## Reading the values

`stats[].values` is positionally parallel to `metric_specs`. Branch on `vtype`, not on
the stat name:

| `vtype` | Shape |
|---|---|
| `count` | A plain number |
| `tset` | A **list** of `{key, value}` — `key.key_type` is `string` or `ipaddr` |
| `sset` | `{count, sum, sum2}` — a sampleset; derive the mean, do not read `sum` as a total |

An `ipaddr` key carries `addr`, `host` (resolved name, may be absent) and `device_oid`.
A `string` key carries `str`.

### The nested `topn_tset` — two unwraps, not one

`ssl_server_detail:key_agreement` is `topn_tset`: **each outer key is a group string, and
its `value` is itself a list of per-client entries.** Verified live:

```json
[{"key": {"key_type": "string", "str": "ECDHE-x25519"},
  "value": [{"key": {"addr": "10.32.1.48", "device_oid": 8589934685,
                     "host": "corp.ad.example.com", "key_type": "ipaddr"}, "value": 23},
            {"key": {"addr": "10.32.1.48", "device_oid": 8589935714,
                     "host": "corp.ad.example.com", "key_type": "ipaddr"}, "value": 26}],
  "vtype": "tset"},
 {"key": {"key_type": "string", "str": "PQC-ECDHE-Kyber-768-x25519"},
  "value": [{"key": {"addr": "10.4.10.43", "device_oid": 8589935282,
                     "host": "kvm-lab-3.internal.example.com", "key_type": "ipaddr"},
             "value": 51145057}],
  "vtype": "tset"}]
```

Code that unwraps once treats the inner list as a scalar and produces nonsense. Walk it
as group → clients.

**Note the two `10.32.1.48` rows.** One client IP, two `device_oid`s — its own per-sensor
copies. **Deduplicate on `addr`.** Counting rows, or summing their values, inflates both
the client count and the session total.

The payoff: this one stat yields the per-client breakdown *and* the named group per
client, so `unique_clients_pqc_observed`, `unique_clients_with_classical_observation` and
`pqc_groups` all come from a single call — and the two client counts are partitions of one
list rather than a difference between two independently-truncated lists.

---

## The `cycle` trap

`cycle` is required and **the wrong value silently returns zeros or nothing at all.**
Verified on 26.3, same object, same window, only `cycle` differing:

| Query | `cycle: "1hr"` | `cycle: "24hr"` |
|---|---|---|
| group 54, `ssl_server:connected`, `total`, `-30d` | `143438958` | `0` |
| device OID, `ssl_server:connected`, `total_by_object`, `-30d` | `51145160` | `sensors: []` |
| device OID, `net:bytes`, `total_by_object`, `-7d` | data | `sensors: []` |

Both failure modes are indistinguishable from real absence — no error, no warning. The
`total_by_object` case is worse: `sensors: []` reads exactly like "that device does not
exist".

**Use `cycle = "1hr"` for windows of days to weeks.** `cycle = "auto"` resolved to `1hr`
on a 30-day window and worked, but pinning it is what makes a result reproducible. If a
query returns zeros or an empty `sensors[]`, **re-run at a different cycle before
concluding anything.**

---

## Truncation — four surfaces, no errors

Every one of these is silent. Inspect the raw response; do not trust a parsed summary.

| Signal | Where | Meaning |
|---|---|---|
| `clamped_limit` | top level | Your `limit` was reduced. `limit = 50000` → `clamped_limit: 5000` |
| `limit_truncation` | top level | A block naming exactly what was dropped |
| `has_more` / `next_offset` | device search, record search | Pagination, a separate concern |

`limit_truncation` is richer than the field name suggests. Verified live with `limit: 3`:

```json
{"effective_limit": 3, "omitted_inner_keys": 44, "omitted_objects": 75,
 "omitted_sensors": 2, "omitted_time_buckets": 35}
```

`omitted_sensors` is the dangerous one — an entire sensor's data can vanish, which on a
console means a whole segment of the estate silently absent from the inventory.

**Scalar queries truncate too.** Verified: 121 OIDs, `total_by_object`, scalar stats, no
`limit` → `effective_limit: 100, omitted_objects: 28`. The default is 100 cells. Always
set `limit` explicitly.

### The 5000 ceiling and the only remedy

The MCP layer hard-caps `limit` at **5000**; higher values are silently clamped and
`-1` is rejected. Cells = `objects × sensors × inner_keys × time_buckets`, which for a
`_detail` query grows fast — 100 servers × 3 sensors × 50 clients is already 15,000.

So above 5000 cells, **chunking the object list is the only remedy, not an alternative.**
Chunk to ~100 OIDs per call and merge. Re-inspect every chunk's response: a chunk can
truncate on inner keys even when the object count is small.

### What truncation does to each number

- **Additive scalars** (`connected`, `post_quantum_kex` per object) — reportable as a
  **lower bound** if still truncated after chunking, labelled as such.
- **Client counts** (`unique_clients_pqc_observed` and
  `unique_clients_with_classical_observation`) — derive **both** directly from the two
  partitions of the single `key_agreement` tset, and each is then a genuine lower bound (a
  client seen with a PQC group *was* seen with one; likewise classical). **Never compute
  either as a set difference** (`all − pqc`): a missing PQC-detail entry then misclassifies
  a real PQC client as classical-only, and the result can be too high *or* too low — not a
  bound in either direction, so it is **`unavailable`, never a floor.** The word "only" is
  itself a completeness claim top-N cannot support — count "clients with a classical
  observation," not "classical-only clients."
- **Distributions** (`key_agreement`, `version` breakdowns) — a top-N by construction.
  Report the named groups as observed and say the tail was not enumerated. Do not
  present the percentages as exhaustive unless the response was clean.
- **`pqc_status`** — from the Step 4 scalar plus the non-detail `key_agreement` groups,
  unaffected by detail truncation. Still reportable when the client columns are not. The
  ML-KEM-vs-Kyber split needs the group names, so a truncated *detail* response does not
  compromise it — but an empty non-detail `key_agreement` does, and then the honest status
  is **`observed_variant_unresolved`** (`variant_resolution = unresolved`), not a guess.

---

## Multi-sensor responses

On a console the response is a **list of per-sensor blocks**, each with its own
`sensor_id` and `stats[]`. The same host appears under a **different OID per sensor**,
and each OID returns only that sensor's view.

**Do not sum across them.** Whether the feeds overlap is not observable from the metric
response, and when they do overlap the sum is inflated. See `scoping.md` for the live
proof and what to report instead.

Also expect a sensor to legitimately return **nothing** — some appliances carry
detections and records but no metric telemetry (`metric_analysis: false` or
`headless_sensor: true` in `licensed_features`). That is a role, not a blind spot; do not
report it as a coverage gap.

---

## Driving the console REST API directly

Above ~50 objects this assessment does not fit in an agent context and has to be scripted
(`SKILL.md`, Operations). Five things about `platform: ecm` differ from what the MCP tool
surface implies, and **every one of them fails as a 404, a 422, a 429 or an empty list —
never as a message naming the problem.** All verified live on 26.3.

| Trap | Symptom | Correct form |
|---|---|---|
| Endpoint spelling | `POST /metrics/total_by_object` → **404** | **`POST /metrics/totalbyobject`** — no underscores |
| Device-group queries are async | Response is `{"xid": 236238, "num_results": 3}` with **no stats** | Poll `GET /metrics/next/<xid>` until `num_results` blocks are collected — one per sensor |
| Record pagination | `offset` → **422** "The configured recordstore does not support the offset parameter" | Pass `context_ttl`, then `POST /records/cursor {cursor, context_ttl}` |
| Filter operands | `{"operand": false}` → **422** "The operand value must be a string, even if the text specifies another data type" | `{"operand": "false"}` — booleans **and numbers** as strings |
| Rate limiting | **429** mid-sweep, silently ending a cursor walk | Retry with backoff, re-mint the bearer token per attempt, ~4 s between cursor pages |

The async-group one is the most dangerous: **per-*device* metric queries return their
blocks inline, while per-*device_group* queries defer.** A collector written against the
device shape and pointed at a group returns cleanly with zero stats, which is
indistinguishable from "this group has no data" — the same failure class as the `cycle`
trap above.

The 429 has the same character. A cursor walk that stops early doesn't error; it just
returns fewer records, so the population looks smaller than it is. Verified: an unbacked-off
sweep stopped at 3,000 of 5,369 records and would have understated the largest finding by
60×. **Always compare records scanned against the response's `total`** and say both numbers
in the report.

Auth is OAuth2 client-credentials — `POST /oauth2/token` with
`grant_type=client_credentials` and HTTP Basic `client_id:client_secret`, then
`Authorization: Bearer <token>` against `/api/v1/…`. Tokens are short-lived; cache with an
expiry margin and re-mint on retry.
