# ExtraHop NPM Domain Knowledge

Metrics model, error classification rules, evidence-sufficiency gates, and health thresholds.

---

## Pre-Assessment Checks

### Data Freshness Gate

Stale data is the worst failure mode — a "healthy" report on stale telemetry misleads the operator into thinking the network is fine when the agent is blind. Query `net:bytes` at capture level for the most recent 5-minute bucket (`bucketing: "timeseries"`, `cycle: "auto"`):

| Most recent data | State | Action |
|---|---|---|
| ≤ 60s old | Fresh | Proceed normally. |
| 60s – 5 min | Slightly stale | Proceed. Note in Key insight. |
| 5–10 min | Stale | Reduce confidence to Medium. Recommend investigating ingestion. |
| > 10 min | Very stale | Return `INSUFFICIENT EVIDENCE` regardless of other metrics. |
| No data | No data | Return `INSUFFICIENT EVIDENCE`; investigate deployment. |

Runs once per assessment, applied to all scopes. For multi-sensor environments, check per sensor; scope the verdict to fresh sensors and call out blind spots.

---

## Metrics Model

Object scopes:

- **Device** (`object_type: "device"`): per-device metrics by OID. Primary scope for host-level analysis.
- **Application** (`object_type: "application"`): admin-defined application groups.
- **Capture** (`object_type: "capture"`): per-sensor aggregates across ALL traffic. Use `extrahop_search_devicegroups` to discover capture OIDs.
  - Bare category names (`http`, `dns`, `ssl`, `tcp`) — no `_server`/`_client` suffix.
  - No latency (`tprocess`), no TCP transport health (rto, rtt, aborted), no error-type breakdowns — those require device-level queries.
- **Device Group** (`object_type: "device_group"`): aggregated across all devices in a group. Same categories as device.

### General Categories (work at any scope)

| Category | Stats | Type | Indicates |
|---|---|---|---|
| **net** | `bytes` | count_rate | Throughput |
| **net** | `pkts_in`, `pkts_out` | count | Packet volume by direction |
| **net** | `external_bytes_in`, `external_bytes_out` | count | Internal vs external traffic |
| **tcp** | `rto_in`, `rto_out` | count | Retransmission timeouts (severe loss) |
| **tcp** | `retrans_out` | count | Fast retransmissions (moderate loss) |
| **tcp** | `rto_multi_in`, `rto_multi_out` | count | **Flow stalls** — multiple consecutive RTOs (most severe) |
| **tcp** | `aborted_in`, `aborted_out` | count | Connection resets |
| **tcp** | `connected`, `accepted` | count | Outbound / inbound connections |
| **tcp** | `rtt`, `setup_time` | dataset | Round-trip / handshake time (requires calc_type) |
| **tcp** | `zwnd_in`, `zwnd_out` | count | Zero-window events (buffer exhaustion) |
| **tcp** | `syn_unanswered_in`, `syn_unanswered_out` | count | Unreachable service signal |
| **tcp** | `rcv_throttle_in`, `rcv_throttle_out` | count | Receive-window throttles |

### Protocol Categories (device-level: MUST use `_server` / `_client` suffix)

| Bare Name | Device Categories | Key Stats |
|---|---|---|
| **http** | `http_server`, `http_client` | `req`, `rsp`, `rsp_error`, `tprocess`, `rsp_ttlb`, `rtt`, `status_code` |
| **dns** | `dns_server`, `dns_client` | `req`, `rsp`, `rsp_error`, `tprocess`, `req_timeout`, `rsp_rcode` |
| **ssl** | `ssl_server`, `ssl_client` | `connected`, `aborted`, `expired_cert`, `self_signed`, `weak_ciphers`, `rtt`, `version` |
| **cifs** (SMB) | `cifs_server`, `cifs_client` | `req`, `rsp`, `rsp_error`, `access_time`, `rtt`, `bytes_read`, `bytes_write` |
| **ldap** | `ldap_server`, `ldap_client` | `req`, `rsp`, `rsp_error`, `tprocess`, `rtt`, `error_msg_short` |
| **kerberos** | `kerberos_server`, `kerberos_client` | `req`, `rsp`, `rsp_error`, `tprocess`, `error_msg`, `account_lockout` |
| **db** | `db_server`, `db_client` | `req`, `rsp`, `rsp_error`, `tprocess`, `rsp_ttlb`, `rtt` |

### Capture-Level Categories (`object_type: "capture"`, bare names)

| Category | Key Stats | Indicates |
|---|---|---|
| **app** | `bytes` (topn_set by L7 Protocol) | Traffic volume by protocol |
| **net** | `bytes`, `pkts`, `external_bytes_in`/`out` | Throughput, internal vs external |
| **tcp** | `desync`, `unidirectional_flows`, `external_accepted` | Network-level anomalies. Capture TCP does NOT include rto, rtt, aborted, setup_time. |
| **http** | `req`, `rsp`, `rsp_error` | Aggregate HTTP. No latency at capture level. |
| **dns** | `rsp`, `rsp_error` | Aggregate DNS. No rcode breakdown at capture level. |
| **ldap**, **kerberos**, **db** | `rsp`, `rsp_error` | Aggregate counts |

### Dataset / Sampleset Metrics

Metrics of type `dataset` (`rtt`, `setup_time`, `tprocess`, `rsp_ttlb`, `access_time`) and `sampleset` require `calc_type`:

- **`calc_type: "mean"`** — returns the mean
- **`calc_type: "percentiles"` with `percentiles: [50, 95]`** — returns p50 and p95. Required for latency assessment.

Without `calc_type`, the API returns raw distributions that aren't directly interpretable.

### Device Roles

Common roles used for weighting and discovery: `http_server`, `db_server`, `dns_server`, `domain_controller`, `file_server`, `load_balancer`, `gateway`, `nat_gateway`, `web_proxy`, `firewall`, `vpn_gateway`, `printer`, `voip_phone`, `wifi_ap`, `pc`, `mobile_device`. For the authoritative list of role values accepted by `extrahop_search_devices`, consult that tool's documentation — passing an unsupported role returns a 400.

---

## Two-Pass Error Classification

Not all protocol "errors" indicate degradation. Many use error responses as normal operation. Always:

1. Query aggregate `rsp_error` (Pass 1).
2. Query the breakdown metric (Pass 2). Classify each error as benign or actionable.
3. Compute final status from the actionable rate.

**Breakdown category naming.** The breakdown is a `topn_set` stat queried via `metric_category` + `key1`. Some breakdown stats live on the base protocol category (`http_server:status_code`, `dns_server:rsp_rcode`, `ldap_server:error_msg_short`, `ssl_server:version`); others exist *only* on the `_detail` variant of the category (`kerberos_server_detail:error_msg`). The names below are the verified categories — use them as written. If unsure for a given firmware, confirm with `extrahop_search_metric_catalog` (search the `stat_name`) rather than guessing the `_detail` suffix on or off, since a wrong category returns no data.

### HTTP — `http_server:status_code` (topn_set, key1: string)

| Code Range | Classification | Notes |
|---|---|---|
| **5xx** | Actionable | Server-side failures impacting users |
| 4xx | Exclude — informational | Client errors, auth challenges, rate limiting |
| 3xx | Exclude — benign | Redirects, cache revalidation |

**HTTP error rate = 5xx / `rsp`**

### DNS — `dns_server:rsp_rcode` (topn_set, key1: string)

| Code | Classification | Notes |
|---|---|---|
| **SERVFAIL** | Actionable | Upstream failure or misconfiguration |
| **FORMERR** | Actionable | Malformed query — client or resolver bug |
| NXDOMAIN | Exclude — benign | Normal with DNSBL, WPAD, AD discovery, reverse-DNS |
| REFUSED | Context-dependent | Normal for authoritative servers refusing recursive queries |

**DNS error rate = (SERVFAIL + FORMERR) / `rsp`**

### Kerberos — `kerberos_server_detail:error_msg` (topn_set, key1: string)

**Benign:** `KDC_ERR_PREAUTH_REQUIRED` (standard pre-auth negotiation; typically the highest-volume "error" and completely normal).

**Actionable:** `KDC_ERR_PREAUTH_FAILED` (wrong password), `KDC_ERR_CLIENT_REVOKED` (account disabled/locked), `KDC_ERR_KEY_EXPIRED` (expired password), `KDC_ERR_C_PRINCIPAL_UNKNOWN` (unknown account), `KDC_ERR_S_PRINCIPAL_UNKNOWN` (unknown service), other policy/lockout/privilege errors.

Also check scalar metrics: `account_lockout`, `user_auth_error`, `computer_auth_error`, `user_policy_error`, `computer_policy_error`.

**Kerberos error rate = actionable / `rsp`**

### LDAP — `ldap_server:error_msg_short` (topn_set, key1: string)

**Benign:** `referral` (normal in multi-domain AD), `noSuchObject` (common in authorized directory enumeration).

**Actionable:** `invalidCredentials`, `insufficientAccessRights`, `unavailable` / `busy`, `operationsError`, `unwillingToPerform`.

**LDAP error rate = actionable / `rsp`**

### SSL/TLS

No single error-rate model. Assess across dimensions:

- **`aborted` / `connected` ratio:** > 5% may indicate handshake failures. First check whether aborts correlate with scanner/health-probe/monitor activity (intentional aborts).
- **`expired_cert`:** Informational — verify renewal in progress.
- **`self_signed`:** Informational. Common on internal services.
- **`weak_ciphers`:** Informational security finding.
- **`version` distribution** (`ssl_server:version`, topn_set): flag TLS 1.0 / 1.1 as security/compliance finding.
- **`client_handshake_failure`** (if available): actionable — cipher/version mismatch indicates real config problem.

---

## Health Thresholds

Apply only after error classification and only when activity gates are met.

### Error Rate Thresholds

| Indicator | Normal | Warning | Degraded |
|---|---|---|---|
| TCP retransmission (per-packet) | < 0.1% | 0.1–1% | > 1% |
| TCP RTO events per connection | < 0.5/conn | 0.5–2/conn | > 2/conn |
| TCP abort ratio | < 2% | 2–10% | > 10% |
| HTTP error rate (5xx only) | < 1% | 1–5% | > 5% |
| DNS error rate (SERVFAIL+FORMERR) | < 0.5% | 0.5–2% | > 2% |
| Kerberos error rate (actionable) | < 1% | 1–5% | > 5% |
| LDAP error rate (actionable) | < 1% | 1–5% | > 5% |
| SSL/TLS abort ratio | < 2% | 2–5% | > 5% |
| Database error rate | < 1% | 1–5% | > 5% |
| SMB/CIFS error rate | < 1% | 1–5% | > 5% |

### Latency Thresholds (`tprocess` p50)

| Protocol | Normal | Warning | Degraded | Notes |
|---|---|---|---|---|
| HTTP — application | < 200ms | 200ms–1s | > 1s | The default |
| HTTP — static / CDN edge | < 50ms | 50–200ms | > 200ms | When role indicates static/caching tier |
| DNS — authoritative | < 5ms | 5–20ms | > 20ms | Answering directly from zones |
| DNS — recursive/forwarding | < 50ms | 50–200ms | > 200ms | Querying upstream |
| Database — OLTP | < 100ms | 100–500ms | > 500ms | Transactional (default) |
| Database — OLAP / DW | < 5s | 5–30s | > 30s | Analytical (see Workload Inference) |
| LDAP | < 50ms | 50–200ms | > 200ms | |
| Kerberos | < 20ms | 20–100ms | > 100ms | |
| SMB (`access_time`) | < 50ms | 50–200ms | > 200ms | |

Workload inference is critical — applying OLTP thresholds to a data warehouse produces false DEGRADED verdicts on every check.

### TCP Transport Thresholds

| Indicator | Normal | Warning | Degraded |
|---|---|---|---|
| RTT | < 2× baseline | 2–3× baseline | > 5× baseline |
| Setup time (p50) | < 100ms | 100–500ms | > 500ms |
| Flow stalls (`rto_multi`) | 0 or near-zero | > 0.1 per 100 conns | > 1 per 100 conns |
| Zero-window events (`zwnd`) | < 1 per 100 conns | 1–10 per 100 conns | > 10 per 100 conns |
| Unanswered SYN ratio | < 1% | 1–5% | > 5% |
| Throughput change | within 2× baseline | 2–5× deviation | > 5× or near-zero |

### TCP Retransmission Math

`rto_out`, `retrans_out`, `connected`, `accepted` are all counts. Two formulas with distinct semantics:

**Form A — events per connection** (use when `pkts_out` unavailable):

```
events_per_conn = (rto_out + retrans_out) / (connected + accepted)
```

Event rate, NOT a probability. Can exceed 1.0 on busy servers — a single congested long-lived connection emits many RTOs. Don't describe as a percentage. Use events-per-connection thresholds.

**Form B — per-packet rate** (preferred when `pkts_out` available):

```
per_packet_rate = rto_out / pkts_out
```

True probability between 0 and 1. Matches textbook packet loss. Use per-packet thresholds.

**Prefer Form B for verdicts.** When Form A and Form B disagree (Form A high, Form B low), report it as a workload finding (long-lived connections), not a transport finding.

**Direction matters.** `rto_in` reflects loss from clients; `rto_out` reflects loss from server. Mixed bidirectional rates can mask single-side issues.

---

## Workload Inference

Several latency thresholds depend on workload type. Run inference once per device, cache for the assessment, note in Key insight.

### Database: OLTP vs OLAP

| Signal | OLTP | OLAP / Data Warehouse |
|---|---|---|
| `rsp_ttlb` p50 | < 200ms | > 500ms (often multi-second) |
| Request rate | Hundreds–thousands/sec | Tens/sec, often bursty |
| Bytes per response | Small (KB) | Large (MB+) |
| `tprocess` p50 baseline | 10–100ms | 1–10s |
| Ports | 1433, 3306, 5432 | Same + 8123 (Clickhouse), 21050 (Impala), 9090 (Vertica) |
| Naming hints | `db-prod`, `oltp-`, `app-db` | `dwh-`, `warehouse-`, `analytics-`, `dbt-` |

**Procedure:** Query `db_server:rsp_ttlb` and `db_server:tprocess` p50 over a recent stable window. Decision tree:

- p50 `rsp_ttlb` < 200ms AND `tprocess` < 100ms → **OLTP**
- p50 `rsp_ttlb` > 500ms AND `tprocess` > 1s → **OLAP**
- In between → **Mixed** — apply OLTP with a note; operator should confirm.

Prefer explicit user-specified workload type when given.

### HTTP: Application vs Static / CDN

Default is application-server (200ms / 1s). Use static-content thresholds (50ms / 200ms) when:

- p50 `tprocess` < 20ms in baseline AND p50 `rsp_ttlb` < 50ms, OR
- Device role `web_proxy`, `cdn_edge`, or `load_balancer` with static backends, OR
- Naming hints: `cdn-`, `cache-`, `static-`, `edge-`.

---

## Volume-Drop Detection

The most dangerous failure mode produces zero errors because zero traffic is flowing. Always check request volume alongside errors and latency.

| Volume vs baseline | Status | Notes |
|---|---|---|
| Within 2× | Normal | Typical variation |
| 2–5× drop or rise | Warning | Volume anomaly; investigate |
| > 5× drop toward zero | **Degraded — silent outage** | Service down, isolated, or in maintenance |
| > 5× rise | Warning — load event | Capacity event or workload shift; check errors/latency still healthy |

A volume-drop verdict can be issued even with normal error rates — that's the point. Category in output: `<protocol>_request_volume`.

**Pair with peer behavior.** When a drop is detected on one device, check whether peers (same role) absorbed the load:

- **Load shifted cleanly** (peer volume up proportionally, peer healthy) → source is silently offline; peer is now SPOF — add to operator actions.
- **No peer pickup** → broader service or client-side issue.
- **Peer overloaded** → cascading failure; escalate severity.

**Baseline gate:** if baseline volume < 100 responses, don't issue a volume-drop verdict — a "5× drop to 0" from a tiny baseline is noise.

---

## HSI Bucket Estimation from Dataset Metrics

`tprocess`, `rtt`, `setup_time`, `access_time` are dataset metrics. To compute HSI buckets without per-sample data:

1. Query `_server:tprocess` with `calc_type: "percentiles"` and a list bracketing T and 4T.
2. Interpolate count below T and count above 4T from the returned percentile values.

### Suggested percentile request

Use `[10, 25, 50, 75, 90, 95, 99]` for all protocols.

| Protocol | T (ms) | 4T (ms) |
|---|---|---|
| HTTP — app | 200 | 800 |
| HTTP — static | 50 | 200 |
| DNS — auth | 5 | 20 |
| DNS — recursive | 50 | 200 |
| DB — OLTP | 100 | 400 |
| DB — OLAP | 5000 | 20000 |
| LDAP | 50 | 200 |
| Kerberos | 20 | 80 |
| SMB | 50 | 200 |

### Interpolation

For target latency L:

1. Find adjacent percentiles `p_low`, `p_high` whose values bracket L.
2. `pct_at_L = p_low_rank + (L - p_low_value) / (p_high_value - p_low_value) × (p_high_rank - p_low_rank)`
3. Count at or below L = `total × pct_at_L / 100`.

### Combining with errors

```
Satisfied   = count(tprocess ≤ T) − count_actionable_errors_with_low_latency
Frustrated  = count_actionable_errors + count(tprocess > 4T AND no_error)
Tolerating  = Total − Satisfied − Frustrated
```

Joint (error × latency) distribution isn't returned. Approximate by assuming errors uniformly distributed across latency — small boundary inaccuracy, acceptable for trend tracking.

### Histograms (newer firmware)

When `calc_type: "histogram"` is available (check `extrahop_search_metric_catalog`), use it — exact counts at bucket boundaries beat interpolated. Percentile interpolation is mildly conservative on long-tailed distributions and can under-count Frustrated on the worst-performing devices.

---

## Evidence Sufficiency

### Minimum Activity Gates

Below these volumes, percentages are noise:

| Protocol | Minimum | If below |
|---|---|---|
| HTTP, DNS, LDAP, Kerberos, CIFS, DB | ≥ 100 `rsp` | Report raw counts; classify Normal with "Low activity — insufficient for rate-based assessment" |
| TCP retransmissions | ≥ 1,000 connections OR ≥ 100K `pkts_out` | Report raw RTO counts; don't compute rate |
| TCP zero windows | ≥ 500 connections | Don't assess zwnd health |
| SSL/TLS | ≥ 50 `connected` | Report raw counts |

### Asymmetric Routing

`tcp:unidirectional_flows` at capture level indicates flows the sensor only saw in one direction — almost always a deployment artifact, making TCP-derived metrics unreliable.

| `unidirectional_flows` / total | Treatment |
|---|---|
| < 10% | Normal — full confidence |
| 10–25% | Reduce confidence to Medium; caveat "asymmetric routing observed" |
| > 25% | Low confidence; don't issue Warning/Degraded based on TCP transport alone for this sensor; recommend investigating sensor deployment |

### Baseline Validity

A baseline is **invalid** when:

- It crosses a maintenance window the assessment window doesn't
- It spans a business-hours / off-hours boundary the assessment doesn't (or vice versa)
- The assessment crosses a weekend boundary the baseline doesn't (or vice versa)
- Baseline data is missing or zero

Invalid baselines → Medium confidence at best.

### Confidence Rollup

| Condition | Confidence |
|---|---|
| All checks pass | **High** |
| Driving category at min gate, OR baseline crosses boundary, OR unidirectional 10–25% | **Medium** |
| Driving category below gate, OR unidirectional > 25%, OR baseline missing | **Low** → if Warning/Degraded would have been issued, downgrade to Insufficient Evidence |

---

## Baseline Selection

### Comparison Method

| Situation | Method |
|---|---|
| Single device, high volume (> 10K rsp), > 7d history | Historical (same-day-last-week) |
| Single device, moderate volume (100–10K rsp) | Peer comparison + historical |
| Single device, low volume (< 100 rsp) | Raw counts only — no rate-based verdict |
| Fleet check | Each device vs fleet median; flag > 2 MAD as outliers |
| First-of-its-kind device (no history) | Peer comparison only |

MAD = median absolute deviation. Compute median of `tprocess` p95 across peers; outliers have `|value − median| > 2 × MAD`.

### Historical Window

| Assessment Window | Preferred Baseline | Fallback |
|---|---|---|
| ≤ 1 hour | Prior 1-hour block | — |
| 1–6 hours | Prior equivalent block | Same hour yesterday |
| 6–24 hours | Same period 7 days ago | Prior equivalent (with caveat) |
| > 24 hours | Same window 7 days ago | Prior equivalent (with caveat) |

Same-day-last-week avoids weekly batch-job boundaries. A Monday-morning prior-equivalent compares to Sunday — usually a poor comparison.

### Meaningful Deviation

Requires **all three**:

1. Percentage change > 2× (rate doubled or halved at minimum)
2. Absolute difference exceeds the activity threshold for that category
3. Baseline itself ≥ activity gate

The third rule prevents reports like "errors up 233% (3 → 10)."

### Peer Comparison Procedure

1. Identify device role via `extrahop_get_device`.
2. Query `extrahop_search_devices` for same role.
3. Compute fleet median and MAD across peers for each shared metric.
4. Flag outliers: value exceeds median + 2 × MAD.
5. Report absolute value AND rank ("4th of 12 peers, 1.8× the fleet median").

Peer comparison answers "is this device worse than its siblings right now?" — distinct from "did this device get worse?"

---

## Multi-Tier Correlation

Most enterprise outages have a single root cause that propagates upward. Before finalizing Warning/Degraded, look for downstream evidence.

| Degrading Category | Check Downstream | Downstream Cause Pattern |
|---|---|---|
| HTTP 5xx on `http_server` | `db_server:tprocess` on backends; `tcp:rto_out` web→db | Backend latency rose at or before HTTP errors |
| HTTP `tprocess` elevated | Same + SSL handshake on outbound | Outbound dependency latency precedes elevation |
| LDAP errors on a DC | Kerberos on same DC; `tcp:rto_out` to replication | If Kerberos also down, treat as single AD root cause |
| Kerberos errors on a DC | LDAP and DNS on same DC; replication | Same AD root cause |
| SMB/CIFS slowness | `tcp:rto_out` and `tcp:zwnd_in` on file server | TCP layer precedes SMB symptoms |
| DB latency on `db_server` | `tcp:rto_out` to replication peers; storage (out-of-band) | Replication or storage as common DB root cause |
| Web proxy / LB 5xx | Pool member health; aborts to specific backends | Single-pool-member failure cascading to LB |

When a downstream cause is identified, upstream verdict still reflects user experience (HTTP 5xx is real) but the report's recommended actions target the downstream tier.

---

## Device Role Relevance Weighting

| Device Role | Primary (drives `overall_status` and HSI_device) | Secondary (reported, doesn't drive status) |
|---|---|---|
| `http_server`, `load_balancer` | HTTP, SSL, TCP latency | net throughput, TCP retransmissions |
| `dns_server` | DNS, TCP | net throughput |
| `domain_controller` | Kerberos, LDAP, DNS | TCP, SSL |
| `file_server` | CIFS/SMB, TCP | net throughput |
| `db_server` | Database, TCP (connections, latency) | net throughput |
| `gateway`, `nat_gateway` | net throughput, TCP | all protocols equally |

`overall_status` logic:

- Max severity across **primary** categories
- Secondary at Warning does NOT elevate above Normal unless primaries also show issues
- Secondary at Degraded elevates to Warning

Only primary categories contribute to HSI_device. Secondary categories report their own per-category HSI separately. Prevents a DC's HTTP management console from dragging down its AD health score.

---

## Account Lockout Findings

`account_lockout` (from `kerberos_server`) gets first-class treatment. A sustained spike maps to one of three real situations:

| Pattern | Probable cause | Priority | Action |
|---|---|---|---|
| Small constant rate, no spike | Misconfigured service accounts with stale credentials | Medium | Identify source accounts; rotate credentials |
| Sudden spike, broad account distribution | **Password spray attack** | **Critical — page security** | Capture source IPs via `extrahop_search_records`; coordinate with SecOps |
| Sudden spike, concentrated on few accounts | Credential testing OR MFA outage forcing password fallback | High | Verify MFA health; check accounts for compromise |
| Coincident with `KDC_ERR_PREAUTH_FAILED` spike | Same as above — failures producing lockouts | High | Treat as single finding (PREAUTH_FAILED is upstream) |

Activity gate: ≥ 5 lockouts in window, OR ≥ 3× baseline rate. Below this, noise.

---

## Sensor Deployment Caveats

Cloud and virtual sensor deployments have failure modes that look like network problems but aren't.

| Signal Pattern | Likely Cause |
|---|---|
| `unidirectional_flows` > 25% sustained, broadly distributed | VPC mirroring loss (AWS/Azure) or SPAN oversubscription |
| `tcp:setup_time` p50 elevated uniformly across all devices on one sensor | Hypervisor CPU steal on the sensor host |
| Low device diversity, low protocol diversity | Overlay encapsulation (NSX/VXLAN/GENEVE) not being decapped |
| Volume of all metrics drops uniformly to near-zero | Sensor disconnected; cross-reference freshness check |

When detected, return `Insufficient Evidence` for affected categories with recommendation to investigate sensor deployment. Don't issue Normal on data that may not be representative.

---

## Enterprise Environment Notes

- **Load balancers:** high `aborted_out` may be intentional (LB resetting connections to unhealthy backends). Check correlation with backend health first.
- **Active Directory cascading:** when a DC's Kerberos is degraded, LDAP almost always is too. Single root cause, not two.
- **NAT gateways:** high connection counts and asymmetric traffic are normal. RTT may be misleading. Focus on throughput and connection success.
- **Reverse proxies / CDN edge:** 5xx on the edge often reflects origin issues. Apply HTTP→backend correlation.
- **Health probes and scanners:** generate background noise (small constant rates of aborts, 4xx, short-lived connections). Don't flag if baseline-consistent.
- **PMTU blackholes:** localized destinations with elevated `rto_out` and small `pkts_out` but normal `connected` counts suggest path-MTU issues (misconfigured VPN/tunnel MTU).
- **Maintenance and batch windows:** weekly batch (Sunday backups, Saturday patching, EOM reporting) skews prior-equivalent baselines. Use same-day-last-week for windows ≥ 24h.
- **Transient routing events:** brief unidirectional-flow spikes during BGP convergence appear as TCP problems. Treat as transient if recovers within window.
- **Microburst-induced retransmissions:** short TCP retrans spike recovering in < 5 min is usually a microburst on a shared link. Temporal pattern analysis catches this; call out the microburst pattern explicitly.

---

## Tool Capability Map

| Tool | If missing | Workaround |
|---|---|---|
| `extrahop_search_devicegroups` | Cannot auto-enumerate sensors | Fall back to device-by-name; ask user for sensor names |
| `extrahop_search_devices` | No fleet discovery by role | Restrict to user-named devices; no protocol fleet or peer comparison |
| `extrahop_get_device` | No role retrieval for weighting | Treat all categories as primary; note ambiguity |
| `extrahop_execute_metric_query` | **Skill cannot function** | Report error; no verdict |
| `extrahop_search_metric_catalog` | Can't verify uncommon metric names | Use known metrics from this reference; flag uncertainty |
| `extrahop_search_records` | No transaction drill-down | Limit to metric level; recommend operator query via ExtraHop UI |
| `extrahop_assign_devicetag_to_devices` / `extrahop_unassign_devicetag_from_devices` | Tagging unavailable | Run report-only; note tags wouldn't persist |
| `extrahop_get_appliance_metadata` | No FQDN for deep-links | Emit reports with plain backticked identifiers; never fabricate URLs |

When a tool is missing, mention it once in Key insight and proceed with what's available. Don't refuse to run.
