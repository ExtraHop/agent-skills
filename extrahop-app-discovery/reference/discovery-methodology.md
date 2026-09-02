# Discovery Methodology

Wire data — the traffic the ExtraHop sensor observes passively at L2–L7 — is the
empirical ground truth for application discovery. Unlike logs (self-reported, easily
altered) or endpoint agents (limited to supported OSes, add overhead), wire data is
observed out-of-band and covers every transaction, session, and flow that crosses the
sensor. Whether an application is on-premises, virtualized, or cloud-native with
traffic mirroring, the wire data is the constant. That is what lets discovery surface
undocumented dependencies, shadow IT, and lateral communication patterns that
traditional tools miss — within the limit that the sensor only sees what crosses it.

All tools below are the `extrahop_*` MCP tools (namespace-prefix if your client
requires it).

---

## Prerequisites — establish environment context first

Run these before discovering specific applications. They prevent false conclusions
from incomplete data.

### Phase 1: Infrastructure baseline

1. **Core services.** `extrahop_search_devices` with role `domain_controller`, then
   `dns_server`, to locate the Active Directory, DNS, and DHCP infrastructure. Almost
   every application depends on these; baseline them first so their traffic isn't
   mistaken for an application tier.
2. **Existing models.** `extrahop_search_devicegroups` with type `user_created` to list
   the groups already defined, and `extrahop_list_devices_in_devicegroup` to inspect a
   group's membership. Report what is already modeled before recommending anything new
   — duplicate groups fragment metrics. (Listing administrator-defined *Application
   objects* is not exposed through the MCP; if the user needs that inventory, point
   them at the `extrahop-rest-api` skill, which generates the `GET /applications` call.)

### Phase 2: Discovery mode awareness (L2 vs L3)

ExtraHop identifies devices two ways:

- **L2 discovery** (MAC-based, default) tracks devices by MAC. Good for DHCP
  environments where IPs change. But in routed or cloud deployments the sensor may see
  the **gateway's MAC** instead of each endpoint, so many distinct servers collapse
  under one "gateway device."
- **L3 discovery** (IP-based) tracks each server by IP. Required for remote/routed
  subnets.

If `extrahop_search_devices` returns a small number of `gateway` devices carrying
disproportionately high `net:bytes` relative to their peers, suspect **gateway
aggregation** — real servers hidden behind a router MAC. Flag this as a finding and
recommend enabling L3 Discovery or Remote Discovery for the affected subnets. Do not
report the aggregate as a single application server.

### Phase 3: Decryption verification

Before HTTP host/URI (Approach 2) or TLS SNI (Approach 3) discovery, confirm the sensor
can see into the payload. With ubiquitous TLS 1.3 and Perfect Forward Secrecy, header
inspection requires decryption.

**Method.** For a candidate device, query both `ssl_server:connected` and
`http_server:req` over the same window. If `connected` shows substantial TLS sessions
but `req` is zero or near-zero, the traffic is encrypted and **not being decrypted**.

When a decryption gap is found:

- Flag it as a primary finding: "TLS traffic on `<device>` is not decrypted — HTTP-layer
  discovery is unavailable for this device."
- Recommend deploying the **ExtraHop Session Key Forwarder** on the application servers,
  or configuring **F5 LTM / Citrix ADC session-key forwarding** if a hardware load
  balancer terminates TLS.
- Fall back to **TLS SNI** discovery (Approach 3) — SNI is sent in cleartext even in
  TLS 1.3 unless Encrypted Client Hello is deployed, which is rare in enterprise — and
  to **behavioral** analysis (Approach 4), which needs no decryption.

---

## Approach 1: VIP / Load Balancer mapping (high-fidelity)

The highest-confidence approach where services are load-balanced. It finds the
public-facing entry points and maps each to its backend pool.

**Step 1 — Identify load-balancer candidates.** Do not rely on `role=load_balancer`
alone; the heuristic classification misses software LBs (NGINX, HAProxy, Envoy), which
often appear as `http_server` or generic Linux devices. Look for **high fan-out both
directions** — a device acting as a server to many clients *and* a client to many
backends:

- `extrahop_search_devices` with role `load_balancer` (catches hardware LBs: F5, Citrix,
  A10).
- `extrahop_search_devices` with role `http_server`, then check whether those devices
  also carry `http_client` metrics (they forward to backends).
- Devices with both `ssl_server:connected` / `http_server:req` (terminating client
  traffic) **and** `ssl_client:connected` / `http_client:req` (initiating backend
  connections).

**Step 2 — Extract application identities from the VIP.** For each confirmed LB, query
`host_http_server_detail` (stat `req`, string key) for the top **Host** headers — each
distinct Host typically maps to a separate application or microservice behind the VIP.
For TLS-terminated services, collect distinct `serverName` (SNI) from `~ssl` records,
and use `ssl_server:version` / `:cipher` topn for the TLS posture.

**Step 3 — Correlate front-end to back-end (the record pivot).** Client-to-VIP and
LB-to-pool-member are **two distinct TCP sessions** in the record store. To find the
pool:

1. `extrahop_search_records` on `~http` where `clientAddr` = the LB's IP **and** `host`
   = the target application's Host header. The `serverAddr` values are the backend pool
   members.
2. If HTTP is undecrypted, `extrahop_search_records` on `~flow` where `senderAddr` = the
   LB IP to list every backend IP it talks to, and group flows by port and temporal
   correlation to separate applications.
3. Look for `X-Forwarded-For` in `~http` records — it traces the original client through
   the proxy chain and confirms the LB→backend relationship.

**Step 4 — Resolve and report.** Resolve backend IPs to devices with
`extrahop_search_devices` (`ipaddr` filter) → `extrahop_get_device`. Report per
application: VIP/entry point, Host or SNI, backend members as plain identifiers, protocols,
request/response volumes, and decryption status.

---

## Approach 2: HTTP Host/URI microservice clustering

When the entry point isn't a load balancer (direct-to-server or container platforms),
cluster HTTP traffic into applications. **Prerequisite:** HTTP decryption active for the
targets (Phase 3) — else fall back to Approach 3 or 4.

**Step 1 — Collect distinct Host headers.** `extrahop_search_records` on `~http` for the
target subnet or environment; extract distinct `host` values. Each unique Host typically
represents a separate application, microservice, or API endpoint. (`host_http_server_detail`
gives the same breakdown at the metric level per server.)

**Step 2 — Sub-group by URI path prefix.** A single Host (e.g. `api.retail.com`) may
serve different backends by path: `/v1/payments` and `/v1/catalog` may be entirely
different container sets. Group first by `host`, then sub-group by the first one or two
URI segments (everything under `/api/v1/checkout/` is the checkout service). This
granularity is essential in Kubernetes, where IP-based grouping is meaningless due to
pod ephemerality.

**Step 3 — Identify serving devices per group.** Collect distinct `serverAddr` from the
`~http` records of each Host+URI group; resolve via `extrahop_search_devices` (`ipaddr`).
In containerized environments IPs may be ephemeral — report IP ranges and naming
patterns rather than individual ephemeral devices.

**Step 4 — Snapshot volume and mix.** Query `http_server:status_code` (topn) for the
serving devices to see the response-code distribution per group. This validates the
grouping and gives an initial picture; for an actual health verdict, hand off to
`extrahop-health-check`.

---

## Approach 3: TLS SNI-based service discovery

For environments where the payload is encrypted but TLS metadata is visible. SNI is sent
in cleartext during the handshake (even TLS 1.3, unless Encrypted Client Hello — rare in
enterprise).

1. `extrahop_search_records` on `~ssl` to collect distinct `serverName` (SNI). Each
   unique SNI typically maps to a distinct service endpoint.
2. Group by SNI; for each, collect the `serverAddr` IPs/devices serving it.
3. Where flows are decrypted, enrich with `~http` records (URI patterns, response
   characteristics).
4. At the metric level, use `ssl_server:version` and `ssl_server:cipher` (topn) on
   candidate devices for the TLS-version and cipher-suite distributions.
5. Flag security-relevant findings as you go: expired certs (`ssl_server:expired_cert`
   > 0), self-signed (`ssl_server:self_signed` > 0), weak TLS versions (`~ssl` `version`
   = SSLv3 / TLSv1 / TLSv1.1, or `ssl_server:version` topn), weak ciphers
   (`ssl_server:weak_ciphers` > 0, or `~ssl` `cipherSuite` with RC4/DES/NULL). See the
   security-hygiene table in `modeling-recommendations.md`.

---

## Approach 4: Behavioral peer grouping (protocol activity scan)

When L7 metadata is unavailable — proprietary protocols, undecrypted traffic, non-HTTP/
TLS services — infer application boundaries from communication patterns. This is the
default when no approach is named.

1. **Find active servers by role.** `extrahop_search_devices` filtered on the key roles
   (`http_server`, `db_server`, `file_server`, `dns_server`, `domain_controller`,
   `mail_server`).
2. **Profile protocol activity per server.** For each device, query aggregate metrics
   across `net`, `tcp`, and whichever protocol categories apply (`http_server`,
   `dns_server`, `ssl_server`, `cifs_server`, …) to build a protocol fingerprint — which
   protocols it speaks and in what volume.
3. **Identify peer clusters.** Devices with similar fingerprints that also talk to a
   common set of backends (databases, message queues) likely share an application tier.
   Use `~flow` records to find connection patterns — three servers all connecting to the
   same database on 3306 are likely one application's web/app tier.
4. **Use the `activity` filter.** `extrahop_search_devices` supports filtering by
   protocol activity (e.g. `activity=extrahop.device.http_server`) to find every device
   speaking a given protocol.
5. **Map lateral dependencies.** For each server, note atypical connections — a web
   server with SMB to an unexpected share, or SSH/RDP into another zone. These are both
   application dependencies and security-hygiene signals; if one looks like an active
   threat, hand off to `extrahop-triage`.

---

## Discovery command parameters

The analyst may append parameters after the discovery request:

- **Approach keyword** — `vip`, `http`, `tls`, `scan` — selects the primary approach
  (Approaches 1–4 respectively; `scan` adds opportunistic checks from 1–3).
- **Target scope** — a CIDR (`10.20.0.0/16`), a role ("web servers"), a device group, or
  a device name — limits discovery to that scope.
- **Vertical hint** — `retail`, `financial`, `healthcare`, `government` — applies the
  matching playbook in `vertical-playbooks.md`.
- **Free-text guidance** — anything else (e.g. "focus on the payment chain," "find what's
  behind the F5") is incorporated.
- If nothing is specified, run a broad behavioral scan (Approach 4) with opportunistic
  VIP, HTTP, and TLS discovery.
