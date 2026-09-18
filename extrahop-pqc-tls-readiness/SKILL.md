---
name: extrahop-pqc-tls-readiness
description: "Assess post-quantum cryptography readiness from ExtraHop RevealX wire data — which TLS and SSH services actually negotiated PQC or hybrid key agreement, which are still on classical RSA/DHE/ECDHE, and which had PQC advertised to them yet negotiated classical anyway. Produces an estate-wide crypto posture summary and a per-server (or per-client) inventory as CSV, a self-contained HTML report, or both. Use whenever the request involves PQC or post-quantum readiness, quantum-safe or quantum-vulnerable TLS, ML-KEM or Kyber adoption, hybrid key agreement, harvest-now-decrypt-later exposure, crypto migration tracking, key-agreement or cipher inventory, weak TLS versions or RSA key sizes, or SSH key-exchange algorithms. Activate on phrasings like 'which servers support PQC', 'assess post-quantum readiness', 'are we quantum-safe', 'PQC adoption report', 'which clients negotiate ML-KEM', 'find servers still using classical key exchange', or 'crypto posture inventory'."
---

# ExtraHop PQC / crypto posture readiness

A sensor sees the **negotiated** key agreement of every TLS and SSH handshake that
crossed the wire. Configuration databases and certificate inventories describe intent;
this skill reports what actually happened.

Answers, in the order they are worth answering:

1. **Estate posture** — what fraction of sessions used PQC, classical ECDHE, DHE, or RSA
   key transport, and on which TLS versions. One cheap call. (Step 2)
2. **Per-service inventory** — which servers negotiated PQC, which did not, session and
   client counts. (Steps 3–4, 6)
3. **The capability gap** — which TLS 1.3 servers had a client *advertise* a PQC group and
   negotiated classical anyway. The strongest negative signal metrics cannot produce — but
   an advertisement, not a proven key-share refusal (RFC 8446 §4.2.8), so a candidate to
   confirm, not a verdict. (Step 5)
4. **SSH** — key-exchange algorithms, where `sntrup`/`mlkem` are already in use. (Step 7)

**Key agreement is one of three axes, and alone it understates the migration.** Report
all three; they cost one extra batched call (Step 2b):

- **Key agreement** — PQC vs classical. What most people mean by "PQC readiness".
- **Authentication** — every RSA/ECDSA certificate is quantum-vulnerable, and cert
  rotation is the long-lead item. Approximate with `keysize` and `cert_pubkey_curve`;
  there is no signature-algorithm metric, so say so rather than implying coverage.
- **Protocol floor** — **TLS 1.2 cannot carry a hybrid PQC group at all.** A server with
  **no TLS 1.3 sessions** could not have negotiated PQC in the window — far more actionable
  than "no PQC observed" and one stat away. But that is an *observation*: label it **"no
  TLS 1.3 observed,"** not "cannot do PQC," because a 1.3-capable server that met only
  TLS 1.2 clients also shows zero 1.3. (A host that is merely *majority* TLS 1.2 but has
  some TLS 1.3 already supports 1.3 — never a blocker. See Step 6.)

> **Observation ≠ capability — the framing that governs every output.**
> `post_quantum_kex > 0` proves a server **can** do PQC. Zero proves nothing: the server
> may be incapable, *or* no peer offered a PQC group in the window. Report **"PQC
> observed" / "no PQC observed"**, never "PQC-ready / not PQC-ready" or
> "capable / incapable". A "no PQC observed" server is a **candidate to investigate**,
> not a remediation item — unless Step 5 shows a client advertised PQC to it and classical
> was negotiated, which raises it to a stronger candidate (still an advertisement, not a
> proven refusal).

> **"PQC observed" is two different findings, and merging them inverts the report.**
> `post_quantum_kex` counts pre-standard **Kyber-768-draft** exactly the same as
> standardized **ML-KEM-768** (FIPS 203). A host on Kyber-draft still has a migration
> ahead of it — the codepoint is being retired — so a single `observed` status quietly
> reclassifies future work as finished work. **Always split the two**, in the per-host
> status *and* in any headline number (`reference/output.md`).
>
> Verified live: 78.6% of sessions were PQC, but 95% of that volume was **two lab hosts on
> Kyber-768-draft** — so the companion rule: **a share of sessions is meaningless without a
> concentration check.** Always report what fraction of PQC volume the top 2–3 hosts carry
> (`reference/output.md`); a single busy box can carry the whole number.

## Load

Read this file, then load only what the step you are on names.

| File | Contents | Load when |
|---|---|---|
| `reference/metrics.md` | Stat names, dimensions, the `topn_tset` shape, truncation surfaces, the `cycle` trap | Before writing any metric query |
| `reference/classification.md` | The `PQC-` prefix rule, named TLS groups, SSH algorithm prefixes, classical-weakness thresholds, `~ssl_open` fields and PQC group codepoints | Before classifying any group name, or before Step 5 |
| `reference/scoping.md` | How to enumerate servers correctly: the CIDR filter, multi-sensor copies, why `device_class` and summing both fail | Before Step 3 |
| `reference/output.md` | Format precedence, CSV spec, HTML spec, the written narrative | Before emitting anything |
| `reference/console-urls.md` | Deep-links into the RevealX console | Before emitting a report that names a device or group |
| `assets/report-template.html` | Self-contained brandable HTML one-pager (an output asset, not context — read only when emitting HTML) | When emitting HTML |

Regulatory timelines (CNSA 2.0), migration-program planning and board-level framing are
**out of scope** for this skill. It produces evidence; let the reader's own program supply
the deadlines.

## Operations

Named by meaning, not by tool. Map each to whatever interface is present — an MCP server
(`execute_metric_query`, possibly namespaced `mcp__extrahop__…`), the `excli` CLI, or
`/api/v1` REST. The live schema wins over anything written here.

| Operation | REST binding |
|---|---|
| `search_devicegroups` | `POST /devicegroups/search` |
| `search_devices` | `POST /devices/search` |
| `query_metrics` | `POST /metrics/total`, `/metrics/totalbyobject` |
| `search_records` | `POST /records/search` |
| `get_device` | `GET /devices/{id}` |
| `get_appliance_metadata` | `GET /extrahop`, `GET /appliances` |
| `search_metric_catalog` | *MCP/CLI only — no direct REST equivalent.* Optional, to verify a stat name; over REST just run the metric query, or read the catalog another way. **Do not map it to `/metrics/next/{xid}`** — that is the async metric-result **polling** endpoint (`reference/metrics.md`), not a catalog search. |

Read-only throughout: metrics and records only, no packets, no state changes. If an
operation is unavailable, say so and continue with what remains — Steps 1–4 and 6 need
only `query_metrics` plus one device enumeration.

> **Above ~50 objects, stop making individual tool calls and drive the API from a
> script.** This assessment routinely reaches a few hundred hosts, and a host has one OID
> *per sensor*: 358 in-scope hosts on this estate meant **551 OIDs × 4 stats × 3 sensor
> blocks**, whose raw responses do not fit in an agent context at all. Chunked
> tool calls do not scale past the low hundreds of cells — they exhaust context long
> before they exhaust the data.
>
> So for Steps 4, 6 and 7 at that size: write a small client, **persist raw responses to
> files**, aggregate with code, and read only the aggregates back. The analysis is
> identical; only the transport changes. If you go this route, the console REST quirks in
> `reference/metrics.md` are mandatory reading — all five of them fail as a 404, a 422, a
> 429 or an *empty list*, never as a message telling you what is wrong.

---

## Procedure

Default window: **30 days** (`from = "-30d"`, `until = 0`) unless the user says otherwise.

**Steps 5 and 6 are deliberately ordered capability-gap-first.** The capability gap is the
highest-value output in the whole assessment and costs one short sweep; the per-host
detail pass is the expensive part, and its status column cannot be finalized without the
Step-5 candidate list anyway. Do not reverse them — you will pay for the expensive pass twice.

### Step 1 — Orient

Confirm what you are connected to and cache it: firmware, whether this is a console
fronting several sensors, and the console FQDN + appliance UUID for deep-links
(`reference/console-urls.md`). Everything downstream depends on the multi-sensor answer.

### Step 2 — Estate posture first, and it is nearly free

**Do not start by enumerating devices.** One `device_group` query returns the whole
estate's key-agreement and TLS-version distribution:

```
query_metrics(
  object_type = "device_group", object_ids = [<TLS Server Activity group id>],
  metric_category = "ssl_server",
  metric_specs = [{name: "key_agreement"}, {name: "version"},
                  {name: "connected"}, {name: "post_quantum_kex"}],
  bucketing = "total", from = "-30d", until = 0, cycle = "1hr")
```

Find the group id with `search_devicegroups(name = "TLS Server", type = "built_in")` —
look for **"TLS Server Activity"**. If it is absent, pass the device OIDs from Step 3
with `bucketing = "total"` instead; the group is a convenience, not a requirement.

> **`cycle` is load-bearing and `24hr` silently returns zeros.** Verified on 26.3: the
> identical query with `cycle = "24hr"` returned `values: [0]` for every sensor while
> `cycle = "1hr"` returned 143,438,958 — and at `total_by_object` it returned
> `sensors: []`, an empty result indistinguishable from "no such device". **Use
> `cycle = "1hr"` for windows of days to weeks.** Never read a zero or an empty
> `sensors[]` as absence without re-running at a different cycle
> (`reference/metrics.md`).

This one call already answers most of what a CISO asks, and it answers it across the
whole estate rather than a top-N of it — but note the distributions are themselves top-N,
so name the groups you saw and do not present the percentages as exhaustive. Read from
it:

- **PQC share** — `post_quantum_kex / connected`.
- **Standardized vs pre-standard** — `PQC-…ML-KEM…` (FIPS 203) vs `PQC-…Kyber…`.
- **Quantum-vulnerable classical** — `ECDHE-*`, `DHE-*`, and especially `RSA-*`, which
  is key *transport*, not forward-secret. `reference/classification.md` has the
  thresholds worth flagging.
- **Version floor** — `TLSv1.0`/`TLSv1.1` present at all is a finding on its own.

**On a console, each sensor returns its own block. Report them per sensor.** Do not sum
them: the feeds may overlap, so a total is not defensible (`reference/scoping.md`).

Lead the report with this. Steps 3+ exist to name the servers behind it.

### Step 2b — Authentication and protocol floor, same call shape

Near-zero marginal cost, and it covers the other two axes:

```
metric_specs = [{name: "keysize"}, {name: "cert_pubkey_curve"},
                {name: "weak_ciphers"}, {name: "cipher"}]
```

`keysize` is keyed by **`intval`**, not string — read `key.intval`. Verified live on this
estate: `1024` (61 sessions — an RSA-1024 certificate still in use), `2048`, `3072`,
`4096`, plus `256`/`384` for EC keys. Thresholds worth flagging are in
`reference/classification.md`.

**`cipher` is for the cipher inventory only — never to infer PQC status.** TLS 1.3 suites
name only the AEAD and hash; key agreement moved to the `key_share` extension. This is
the single most common analytical error in PQC reporting.

### Step 3 — Enumerate the servers in scope

Full method and its traps in **`reference/scoping.md`** — read it, because the two
obvious approaches are both wrong. In short:

- **Enumerate the full activity population first, then classify by locality — don't lead
  with a CIDR predicate.** A `search_devices(… AND ipaddr = <CIDR>)` filter can only match
  a device that *has* an IP, so it silently drops the ~15% of members with no IP before the
  display-name fallback ever applies. Enumerate the whole group, classify IP-bearing devices
  against the internal ranges, and keep the no-IP devices in an explicit `scope_unknown`
  bucket. And scope by CIDR/locality, **not `device_class`** — discarding
  `device_class: "remote"` looks like an external filter and is not one (verified live, 920
  of 923 `remote` devices were RFC1918).
- **Read the operator's own definition of "internal" first** (`GET /networklocalities`)
  and prefer it over an RFC1918 guess.
- **The same host appears under several OIDs, one per sensor that discovered it. Never
  sum their metrics** — the feeds can carry the same sessions. Verified live: 50
  distinct sessions to one server appeared as 100 records, all 50 seen by both sensors.
  Report the **per-sensor maximum** and name the sensors, or report per sensor.

### Step 4 — Per-server scalars

```
query_metrics(object_type = "device", object_ids = [<OIDs>],
  metric_category = "ssl_server",
  metric_specs = [{name: "connected"}, {name: "post_quantum_kex"}],
  bucketing = "total_by_object", from = "-30d", until = 0,
  cycle = "1hr", limit = 5000)
```

- `connected > 0` → active as a TLS server in the window. `connected == 0` or absent for
  every one of a host's OIDs → drop it. Judge the host, not a single OID.
- `post_quantum_kex > 0` → **PQC observed.** Firm positive — but this scalar does not say
  *which* PQC, and ML-KEM vs Kyber-draft is a reportable difference. Resolve it
  from `key_agreement` (Step 6, or Step 2's estate distribution) and carry it into the
  status: **`observed_mlkem`** (ML-KEM, the FIPS 203 primitive) vs **`observed_kyber_draft`**
  (pre-standard, now obsolete). If the group names came back empty, the honest status is
  **`observed_variant_unresolved`** — not a guess.
- `post_quantum_kex == 0` → **none observed**. Step 5 is what turns this into a real
  finding.

**Check every response for `clamped_limit` and `limit_truncation` and chunk when either
appears.** Even scalar `total_by_object` truncates — verified: 121 OIDs with no `limit`
returned `effective_limit: 100, omitted_objects: 28`, silently. Details and the full
truncation-surface list in `reference/metrics.md`.

### Step 5 — The capability gap: advertised vs negotiated

**This is the step that makes the report actionable, and metrics cannot do it.** Metrics
record only what was negotiated, so they cannot distinguish "the client advertised PQC and
got classical back" from "no client ever advertised it". `~ssl_open` records carry the
client's `supported_groups` advertisement:

```
search_records(types = ["~ssl_open"], from = "-6h", until = 0,
  limit = 1000, context_ttl = 600000,   # context_ttl is REST-only — see the pagination note
  filter = {and: [ {serverIsExternal = false},
                   {isPostQuantumKeyAgreement = false},
                   {keyAgreement exists},
                   {version = "TLSv1.3"},
                   {supportedGroupsHex ~ "<codepoint>"} ]})
```

> **Cursoring the full population is a REST-only capability — the MCP `search_records` tool
> cannot do it, and neither the cursor nor a `total` count is reachable through it.**
> Verified live on 26.3: the MCP tool exposes `limit`/`offset` and returns
> `has_more`/`next_offset` with **no `total`**, and passing `offset` **422s** on this
> recordstore ("specify the `context_ttl` parameter, then `POST /records/cursor`"). The
> `context_ttl` argument above and the cursor walk exist only on the REST path
> (`reference/metrics.md`). So: **to cursor the complete set and read a population `total`,
> drive `/records/search` + `/records/cursor` over REST** (the same script the Operations
> note already calls for above ~50 objects). Through the MCP tool you get a **capped
> sample** — take a single `limit`-bounded page, label it a sample, and report the page
> size and `has_more`, since no `total` is available to state the population against.

`supportedGroupsHex` is the client's `supported_groups` extension as concatenated 4-hex
codepoints. A record where the client advertised a PQC codepoint but
`isPostQuantumKeyAgreement` is `false` means **the client offered PQC support and classical
was negotiated** — a strong signal worth investigating, but read the caveats below
before you call it a decline.

> **`supported_groups` is an advertisement, not a key share — it does not prove the client
> offered a PQC key.** TLS 1.3 lets the `key_share` extension carry a *subset* of
> `supported_groups` (RFC 8446 §4.2.8). A client routinely advertises ML-KEM in
> `supported_groups` yet sends only an X25519 `key_share`; the server then selects X25519
> without ever rejecting PQC, and with no HelloRetryRequest. **Records expose the advertised
> groups (`supportedGroupsHex`) and the extension *types* present (`clientExtensionsHex`),
> but not the `key_share` group contents and not a HRR indicator** — verified live on 26.3.
> So this signal cannot be promoted to "the server refused a PQC key." Report it as
> **"client advertised PQC, classical negotiated"**, rank it, and recommend confirming the
> server's configured groups out of band. A definitive decline needs an observed PQC
> `key_share` or a HelloRetryRequest, neither of which is in the record today.

> **Filter to `version = "TLSv1.3"`, or a TLS 1.2 session becomes a phantom decline.** A
> hybrid PQC group exists only in TLS 1.3 (`reference/classification.md`), so a TLS 1.2
> session that advertised `11ec` never *could* negotiate it — the server did not decline,
> the protocol forbade it. Without the version filter these dominate the result and invert
> the finding. **Verified live: the single widest-exposure "decline" in this estate,
> `ldap-hq.internal.example.com`, is a TLS 1.2 service.** A TLS 1.2 advertisement belongs in the
> structural-floor bucket (Step 6 / no TLS 1.3 observed), *not* in the decline list. If you
> collect them without the filter, split them out and report them as protocol-floor, and
> say how many of the raw hits were TLS 1.2.

> **Four separate defects live in the obvious version of this query. All of them distort
> the count, and none of them errors.**
>
> 1. **One codepoint is not the offer surface.** Several ML-KEM and Kyber-draft hybrid
>    codepoints exist and the IANA registry keeps growing — **loop the query over the whole
>    current PQC set, not just `11ec`.** The list, and the authoritative registry link, are
>    in `reference/classification.md`; treat the five verified-on-26.3 codepoints as a
>    subset, not the whole surface. On this estate every codepoint other than `11ec`
>    returned zero, which is luck, not coverage: a single-codepoint query that happens to
>    pick an empty one reports a clean estate.
> 2. **`~` is a substring match against a concatenated hex string, so it produces false
>    positives.** `supportedGroupsHex ~ "11ec"` matches `…0011ec00…` — a boundary spanning
>    two unrelated codepoints. **Re-parse every returned value into 4-character-aligned
>    pairs client-side and confirm the codepoint sits on an alignment boundary**; discard
>    the record if it does not.
> 3. **`limit = 300` against this filter is a sample, not a finding list.** The filter is
>    narrow enough that the whole population is cheap — **cursor the complete set**
>    (`context_ttl` + `POST /records/cursor`; `offset` is rejected outright, see
>    `reference/metrics.md`) and say how many records you scanned. Verified live: the true
>    population was **5,369 records → 8 declining servers**. At `limit = 300` I found 5 of
>    the 8 and understated the largest by 60×. If you genuinely cannot cursor it all,
>    label the output a sample and give the population size from the response `total`.
> 4. **The same session arrives once per sensor — deduplicate before you count anything.**
>    On a console each appliance that saw the handshake emits its own record, and looping
>    over five codepoints can also return one record more than once. Both inflate the
>    matching-record total, the per-server decline count, and the client ranking.
>    **Deduplicate on a stable session identity — `(flowId, clientPort)` — unioned across
>    appliances and across the codepoint loop, before aggregating.** Verified live: four
>    consecutive raw hits were two sessions, `flowId b96688fb8f575c4c` and
>    `bec0ec31725fc7ec`, each captured by two appliances (`serverExtensionsHex`, ports and
>    key agreement identical). Count distinct sessions, then distinct servers, then
>    distinct clients — never raw record rows.

> **Require `keyAgreement exists`.** Without it the result fills with handshakes where
> no ServerHello was observed — verified: 11 of 200 records had no `keyAgreement` and no
> `cipherSuite`, which is a truncated capture, not a decline. Counting those invents
> findings.

> **Reconcile these servers against the Step 3 scope — never silently drop the ones that
> don't match.** Records are scoped by `serverIsExternal`, the inventory by group
> membership and CIDR, so the two populations are *not* the same set, and this
> high-value finding class is the one most likely to fall outside the table.
> Verified live: `ldap-01.internal.example.com` negotiated classical after a hybrid group
> was advertised by **26 distinct clients** — the widest client exposure of any such server
> in the estate — and is not a member of the `TLS Server Activity` group, so a table-driven
> report would have omitted it entirely. **Report these unmatched servers explicitly,
> saying they sit outside the inventory scope and why.**

Records are retention-bounded and far heavier than metrics, so scope this to a **short
window** and let it qualify the Step 4/6 list rather than replace it. A 6-hour window was
enough to surface 8 distinct internal servers that negotiated classical after a PQC
advertisement here — of which only the TLS 1.3 subset is a candidate downgrade; the TLS 1.2
ones are protocol-floor, not declines. Report the TLS 1.3 "advertised-PQC, classical
negotiated" servers as their own tier, above the "no PQC observed" candidates and below the
firm positives — and label it as an advertisement-level signal, not a proven key-share
refusal (see the key_share caveat above).

### Step 6 — Per-server detail: clients and the groups they used

One call gives both the per-client breakdown *and* which named group each client used,
because `ssl_server_detail:key_agreement` is a **nested `topn_tset`** (string group ×
client IP) — not the flat list the metric name suggests:

```
query_metrics(object_type = "device", object_ids = [<confirmed OIDs>],
  metric_category = "ssl_server_detail",
  metric_specs = [{name: "key_agreement"}, {name: "connected"}],
  bucketing = "total_by_object", from = "-30d", until = 0,
  cycle = "1hr", limit = 5000)

# and, per host, from the non-detail category — groups + version breakdown
query_metrics(object_type = "device", object_ids = [<confirmed OIDs>],
  metric_category = "ssl_server",
  metric_specs = [{name: "key_agreement"}, {name: "version"}],
  bucketing = "total_by_object", from = "-30d", until = 0,
  cycle = "1hr", limit = 5000)
```

Unwrap twice: outer key is the group string, its `value` is a **list** of `{key: {addr,
host, device_oid}, value}`. `reference/metrics.md` has the shape and the walk.

Count clients by **`addr`**, unioned across the host's OIDs and `sensors[]` blocks — one
client IP legitimately appears under two `device_oid`s (its own per-sensor copies).
Verified live on `kvm-lab-1`: `10.32.1.48` appeared under OIDs `8589934685` and
`8589935714`; counting rows would double it.

Classify each group by the **`PQC-` prefix** (`reference/classification.md`) to get
`unique_clients_pqc_observed`, `unique_clients_with_classical_observation` and a
`pqc_groups` cell in one pass. **The
group strings here are also what resolve `observed_mlkem` vs
`observed_kyber_draft`** for the Step 4 status — match `ML-KEM` vs `Kyber` within the
`PQC-` prefixed names. This pass is the cheapest place to get it per host; Step 2's
distribution gives it only estate-wide.

`{name: "version"}` rides along in the second call for free, and the per-host TLS-version
breakdown is what identifies the **structural floor**. Be precise about what the breakdown
proves: a hybrid PQC group requires TLS 1.3, so a host with **no TLS 1.3 sessions at all**
is structurally ineligible until it supports 1.3 — but a host that is *majority* TLS 1.2
with even a sliver of TLS 1.3 **already supports 1.3** and may already negotiate PQC. Do
not call the latter a blocker; the version mix describes sessions and peer behavior, not
the server's capability ceiling. **Classify individual TLS 1.2 sessions as ineligible, but
label a *host* only as "no TLS 1.3 observed" — never "cannot do PQC."** Even zero observed
TLS 1.3 proves only that no PQC could have been negotiated *in this window*, not that the
server is incapable of 1.3 (it may have met only TLS 1.2 clients); confirm the configured
maximum protocol version out of band before treating it as a hard blocker. This "no TLS 1.3
observed" bucket is usually the largest actionable one in the report (verified live: 100
hosts, 26.1M sessions).

> **Every detail client count is a top-N observation, not a census — label it `≥`.**
> Three compounding reasons, all verified:
>
> 1. **Truncation is not always flagged.** Same query, same device, varying only `limit`:
>    `limit: 2` returned exactly 2 client keys with **no `clamped_limit` and no
>    `limit_truncation`**, when the complete set (at `limit: 5000`) was 4. Flags alone
>    cannot detect this. **Add the rule flags can't give you: if the number of inner keys
>    returned for a stat is `>= limit`, treat it as truncated regardless of flags.**
> 2. **The datastore stores top-N per cycle.** A 30-day total at `cycle: 1hr` aggregates
>    ~720 hourly top-N sets computed at write time. A client that never entered any
>    single hour's top-N is absent and **no `limit` can recover it.**
> 3. **Set differences break the bound in both directions.** `unique_clients_non_pqc =
>    all − pqc` turns a *missing* PQC entry into a *false* non-PQC client (an overcount),
>    and a client whose PQC tuple survived top-N while its classical tuple was dropped is
>    missed (an undercount). A value that can be too high *or* too low is not a floor and
>    must never be published as a lower bound. It also invents the word "only" — a
>    completeness claim top-N cannot back.
>
> So: derive both counts from the **single `key_agreement` tset** above, where PQC and
> classical are partitions of one list rather than a difference of two — each partition is
> then a genuine lower bound (a client seen with a PQC group *was* seen with one). Report
> them as lower bounds (`≥ 41`) and name the columns for what they are
> (`unique_clients_pqc_observed`, `unique_clients_with_classical_observation` — not
> "classical-only"). Cross-check per server: **if scalar `connected` greatly exceeds the
> sum of the detail values, the detail list is incomplete** even with no flag. If it is
> incomplete and you cannot bound it, emit `unavailable` for both columns. The **PQC
> status** itself comes from the Step 4 scalar plus the non-detail `key_agreement` groups,
> and is unaffected by detail truncation throughout.
>
> Verified live: max inner keys per group was **7** against a `limit` of 5000, so nothing
> truncated on this estate — but the counts are *still* lower bounds, because reason 2
> above is a property of the datastore, not of your `limit`. **A clean response does not
> upgrade a top-N to a census.**

### Step 7 — SSH

SSH negotiates algorithms directly, so it is the cleanest PQC signal in the estate — and
it has **no `post_quantum_kex` counter**. You must classify by algorithm name.

```
query_metrics(object_type = "device_group", object_ids = [<group id>],
  metric_category = "ssh_server",
  metric_specs = [{name: "kex_algorithm"}, {name: "sessions"}, {name: "cipher"}],
  bucketing = "total", from = "-30d", until = 0, cycle = "1hr")
```

> **The SSH session denominator is `sessions`, not `connected`.** `ssh_server:connected`
> does not exist and the query fails with a bare `400` naming nothing. The TLS categories
> use `connected`; the SSH ones use `sessions`. Full stat list in `reference/metrics.md`.

`sntrup*` and `mlkem*` are post-quantum; `curve25519-sha256`, `ecdh-sha2-*` and
`diffie-hellman-*` are not (`reference/classification.md`). `cipher` is worth pulling in
the same call — it is where the classical remainder shows itself. Per-peer breakdown is
`ssh_server_detail:kex_algorithm`, also a `topn_tset`. Mirror with `ssh_client*` for the
client side.

### Step 8 — Client side (cheap at group level; do it)

Server-side asks "can my servers accept PQC?"; the client side asks **"which of my
endpoints can initiate it?"** — usually the more actionable question, and the one that
explains why a server saw no PQC.

**At group level this is one call and it mirrors the entire server-side story**, so run it
by default rather than treating it as optional: same shape as Step 2 against **"TLS Client
Activity"** (`ssl_client`, `key_agreement` — a flat string distribution keyed by group
name, exactly like the server side). Verified live, it independently surfaced the same
Kyber-dominance, the same `RSA-2048` key transport (14,472 sessions) and the same TLS 1.0
residue.

> **`ssl_client:key_agreement` has no server-IP key — do not try to read `addr` from it.**
> It is a non-detail `topn` string distribution keyed by group name. The per-*server*
> breakdown lives in **`ssl_client_detail:key_agreement`**, a `topn_tset` whose inner key
> is the server `addr` (`reference/metrics.md`). Parse `addr` only from the `_detail`
> response.

The **per-client** inventory (`ssl_client_detail`, Steps 3–6 against group 53) is the
expensive one — that stays opportunistic, for when the user asks about endpoints,
clients, or who needs upgrading.

### Step 9 — Emit

Per `reference/output.md`: format precedence (user's choice → ask when interactive → CSV),
CSV and HTML specs, and the narrative. Deep-link devices and groups per
`reference/console-urls.md`. Lead with Step 2's estate posture, then the TLS 1.3
advertised-PQC/classical-negotiated servers, then the inventory.

---

## Guardrails

- **Never fabricate.** No invented device, IP, session count, group name, percentage or
  console URL. No FQDN obtained → emit the report unlinked.
- **A zero or an empty result is not absence.** Rule out the wrong `cycle`, truncation, a
  metrics-less sensor, and record retention before concluding a service is silent.
- **Never sum across a host's per-sensor OIDs** — overlapping feeds double-count. Report the
  per-sensor max and name the sensors (`reference/scoping.md`).
- **Never dedupe hosts on IP.** DHCP, NAT and VIP failover recycle addresses; use
  `extrahop_id`/MAC.
- **Count distinct client IPs (`addr`), not sessions**, in the client columns — and say so.
- **Exclude L2 aggregates.** Drop `device_class: "gateway"` and any `is_l3: false` device
  with no IP — a MAC-keyed aggregate double-counts the real server (`reference/scoping.md`).
- **Client counts are top-N lower bounds, never a census** (Step 6). A set-difference count
  that cannot be bounded is `unavailable`, never a floor.
- **A cipher suite does not tell you the key agreement.** TLS 1.3 suites name only the AEAD
  and hash; never infer PQC status from `cipher` — use `key_agreement`/`post_quantum_kex`.
- **Never publish a bare PQC share.** Report the concentration (top 2–3 hosts' fraction of
  PQC volume) alongside it and split ML-KEM from Kyber — one busy host can carry the number.
- **Never present a record-derived count without its population.** Distinct sessions scanned
  vs the response `total`; a capped query is a sample, not a findings list.
- **Deduplicate records on `(flowId, clientPort)` before counting** (Step 5) — the same
  session arrives once per sensor and once per matched codepoint.
- **`supported_groups` is an advertisement, not a key share** (RFC 8446 §4.2.8). Advertised
  PQC + classical negotiated is a candidate, not a proven refusal; a TLS 1.2 session is
  never a decline (protocol-floor).
- **Never call a host "cannot do PQC" from wire data.** A version mix proves nothing, and
  even zero *observed* TLS 1.3 means only "none negotiable in this window" — report "no TLS
  1.3 observed" and confirm the configured max version out of band.
- **Never drop a Step-5 server for failing to match the inventory** — records and the
  inventory are scoped differently; report it flagged out-of-scope.
