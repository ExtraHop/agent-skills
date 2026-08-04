# Diagnostic Playbooks

Multi-step recipes for common root-cause patterns. Run when a Pass-1 assessment flags Warning or Degraded, before finalizing the verdict. Goal: follow the chain of causation downward to the dependency that's actually broken rather than reporting symptoms at every tier.

Each playbook starts from a symptom and walks queries that confirm or rule out a downstream cause. Run steps sequentially. If a step confirms downstream cause, stop and finalize with root-cause attribution. If a step rules it out, continue.

---

## Playbook 1: HTTP 5xx Elevated on a Web Tier

**Symptom:** `http_server:status_code` shows 5xx rate above 1% on one or more web/app servers; baseline below 0.5%.

### Step 1 — Latency on the same web server

Query `http_server:tprocess` p50 and p95 with baseline.

- p95 also elevated, rose at or before 5xx onset → server is slow, not just erroring. Continue.
- Latency normal, errors spiking → application-layer fault (bad deploy, config, downstream API returning errors quickly). Skip to Step 5.

### Step 2 — Backend database latency

For each `db_server` the web server communicates with (identify via `tcp:connected` peer breakdown or known topology), query `db_server:tprocess` p50/p95 with baseline.

- DB p95 rose at or before HTTP onset → likely DB root cause. Apply Playbook 3 on the DB.
- DB normal → continue.

### Step 3 — Outbound dependency latency

Query SSL handshake time and `http_client:tprocess` on the web server for outbound API calls.

- Elevated → third-party API or internal microservice is slow.
- Normal → continue.

### Step 4 — TCP transport to backends

Query `tcp:rto_out` from web server to each significant peer, plus `tcp:zwnd_in` on the web server.

- High `rto_out` to specific peer → network path issue to that backend.
- High `zwnd_in` → web server's receive buffers saturating (CPU/memory pressure on web server).

### Step 5 — Single-server isolation

Compare against other members of the same web tier.

- This server alone → server-level fault. Operator should inspect application logs and recent deploys.
- Whole tier → upstream LB, shared dependency, or external load event.

### Verdict

- Downstream cause confirmed → upstream verdict (Warning/Degraded on web tier) stands; multi-tier attribution applied; primary remediation targets downstream tier.
- No downstream cause → web tier is the originating fault; remediation targets the web server itself.

---

## Playbook 2: AD Auth Symptoms on a Domain Controller

**Symptom:** Kerberos actionable errors > 1%, OR LDAP actionable errors > 1%, OR `account_lockout` non-trivial.

### Step 1 — Co-occurrence check

Always query Kerberos AND LDAP on the same DC together, even if only one was flagged. AD subsystems share infrastructure (NTDS, replication, sysvol).

- Both showing actionable errors → AD-wide issue on this DC. **One** finding, not two.
- Only Kerberos → see Step 2.
- Only LDAP → see Step 3.

### Step 2 — Kerberos-specific causes

- `account_lockout` spiking → password-spray attack or misconfigured service account with stale credentials. Flag for security team.
- `KDC_ERR_S_PRINCIPAL_UNKNOWN` spiking → SPN registration problem (recent rename or migration).
- `KDC_ERR_KEY_EXPIRED` spiking → batch of expired passwords (post-policy-change).
- `KDC_ERR_PREAUTH_FAILED` spiking with low account_lockout → end-user password issues, possibly MFA outage forcing fallback.

### Step 3 — LDAP-specific causes

- `invalidCredentials` spike → application using stale service account credentials (deployment regression).
- `unavailable` / `busy` → DC overload. Check `tcp:accepted` and DC CPU out-of-band.
- `operationsError` → NTDS/replication problem. Check DC replication health out-of-band.

### Step 4 — DC infrastructure check

Query `tcp:rto_out` from the DC to other DCs (replication partners) and to the network. Query `dns_server` on the same DC (DCs almost always also serve DNS).

- High `rto_out` to replication partners → replication network issue, likely cascading.
- DNS on same DC also degraded → DC-wide infrastructure problem (storage, NIC, virtualization host).

### Verdict

Consolidate Kerberos + LDAP on the same DC into one "AD services" finding. Don't double-count (use higher severity, weighted as primary).

---

## Playbook 3: Database Server Latency Elevated

**Symptom:** `db_server:tprocess` p95 above warning threshold, sustained.

### Step 1 — TCP layer to the DB

Query `tcp:rto_in`, `tcp:rto_out`, `tcp:zwnd_in`, `tcp:zwnd_out` on the DB server.

- High `rto_in/out` → network path to/from DB is lossy. Check switch/NIC out-of-band.
- High `zwnd_in` → clients can't drain responses fast enough (client-side CPU pressure or undersized buffers).
- High `zwnd_out` → DB sending faster than network can absorb, or receiver flow-controlling.
- All TCP normal → not a network/transport issue. Continue.

### Step 2 — Replication health

Query `tcp:rto_out` from DB to replication peers. Query `db_client:tprocess` from DB toward other DB hosts.

- Elevated → replication backlog (common cause of sudden DB slowdown with sync replication).
- Normal → continue.

### Step 3 — Workload pattern

Query `db_server:rsp_ttlb` p95 with baseline; `db_server:bytes_out` if available.

- `rsp_ttlb` elevated proportionally to `tprocess` → result sets larger than usual (missing index, runaway query).
- `tprocess` elevated but `rsp_ttlb` normal → server-side processing only (CPU-bound, locking).

### Step 4 — Single-DB isolation

- This DB alone → instance-level issue (locks, plan regression, storage).
- Multiple DBs → shared storage, shared SAN, or hypervisor.

### Verdict

DB latency is rarely a network problem. If TCP layer is clean, recommend operator engage DBA team; flag as external action rather than spending more agent cycles.

---

## Playbook 4: TCP Retransmissions Elevated on a Segment

**Symptom:** Capture-level `(rto_out + retrans_out) / pkts_out` > 1%, sustained.

### Step 1 — Asymmetric routing ruleout

**Most common false positive for capture-level TCP findings.** Query `tcp:unidirectional_flows`.

- > 25% unidirectional → sensor isn't seeing return traffic for many flows. **Do not issue Warning/Degraded.** Recommend investigating sensor deployment / SPAN config.
- 10–25% → reduce confidence to Medium, add caveat.
- < 10% → proceed.

### Step 2 — Localize to direction

Compare `rto_out` vs `rto_in` at capture level.

- Mostly `rto_out` → loss on paths leaving this segment (downstream of sensor).
- Mostly `rto_in` → loss on paths entering (upstream of sensor).
- Balanced → bidirectional issue, possibly the segment itself.

### Step 3 — Localize to devices

Drill into top-N devices by `tcp:rto_out` count.

- Concentrated on one peer → likely single bad NIC, link, or PMTU issue. Apply Step 4.
- Spread across many peers → segment-level (uplink congestion, faulty switch, duplex mismatch).

### Step 4 — PMTU blackhole check

For peers with concentrated `rto_out`: look for the signature of a few large packets failing repeatedly while small packets succeed (often visible as long-lived connections with frequent RTOs but low byte counts).

- Pattern matches → likely PMTU blackhole (VPN/tunnel MTU below path MTU with ICMP "fragmentation needed" dropped).
- No match → general path congestion or hardware fault.

### Verdict

A network-segment retransmission verdict should always include the localization (out vs in, concentrated vs spread) — that's what tells the operator where to look.

---

## Playbook 5: SMB/CIFS Slowness on a File Server

**Symptom:** `cifs_server:access_time` p50 above 50ms (warning) or 200ms (degraded), sustained.

### Step 1 — TCP transport check

Query `tcp:rto_out` and `tcp:zwnd_in` on the file server.

- Elevated `rto_out` to clients → network path problem; SMB is the victim, not the cause.
- Elevated `zwnd_in` → file server can't keep up. Storage or CPU bound.

### Step 2 — Read vs write breakdown

Query `cifs_server:bytes_read` and `bytes_write`.

- Heavy write + slow access_time → storage write latency.
- Heavy read + slow access_time → cold cache or storage read latency.
- Balanced → general storage subsystem issue.

### Step 3 — Per-client isolation

Use `extrahop_search_records` if degradation is confirmed and window ≤ 7d. Filter for slow SMB transactions.

- Concentrated on specific clients → client-side (large directory enumeration, AV scanning shares).
- Spread → server-side issue.

### Verdict

SMB latency is usually a storage problem. Recommend operator engage storage team once TCP is ruled out.

---

## Playbook 6: DNS Resolution Degraded

**Symptom:** `dns_server:rsp_rcode` actionable rate (SERVFAIL + FORMERR) > 0.5%, OR `dns_server:tprocess` elevated above threshold.

### Step 1 — Authoritative vs recursive

Determine the DNS server's role and apply the correct threshold band (see `domain-knowledge.md` → Latency Thresholds).

### Step 2 — SERVFAIL root cause

If SERVFAIL dominates and the server is recursive:

- Query `tcp:rto_out` from DNS server to public internet (or to upstream resolvers if forwarding).
- Elevated → upstream connectivity issue. DNS server itself is healthy; its upstream is broken.
- Normal → DNS-software-level issue (DNSSEC validation failure, upstream NXDOMAIN floods, cache poisoning protection rejecting answers).

### Step 3 — Latency cause

If `tprocess` elevated but errors normal:

- Recursive: check upstream RTT. Slow upstream = slow recursion (often transient routing/peering).
- Authoritative: should be single-digit ms. Elevation suggests resource exhaustion. Check `tcp:zwnd_in` and CPU out-of-band.

### Step 4 — Fleet comparison

- This server alone → instance-level.
- Whole fleet → shared upstream (recursive) or shared infrastructure (authoritative).

### Verdict

DNS is high-impact — degradation cascades. Even Warning-level findings should produce a follow-up drill-down, since blast radius is large.

---

## When to Stop Drilling

- A downstream root cause is confirmed (finalize the verdict)
- Three playbook steps have produced "normal" results (further drilling unlikely to find anything)
- A category needs out-of-band investigation (storage, CPU, application logs) — recommend operator action and stop
- Token budget approaching limit (a finalized verdict beats an incomplete one)

Prefer finalizing a verdict over endless exploration. The user can ask follow-ups; an incomplete first answer is worse than a confident answer that scopes its own limits.
