---
name: extrahop-app-discovery
description: Discover and map enterprise applications based on network traffic analyzed by ExtraHop RevealX. Recommend modeling discovered applications in the ExtraHop platform with device tags and device groups. Use whenever the user wants to inventory applications or services, find out "what's running on the network," map an application's tiers (web/app/database), trace the backend server pool behind a load balancer or VIP, identify services by HTTP host/URI or TLS SNI, discover undocumented dependencies or shadow IT, or get device-group and tagging recommendations for an application. Activate on phrasings like "discover my apps," "what applications are on this subnet," "map the checkout service," "what's behind this VIP," "inventory the services in 10.20.0.0/16," "find all the web apps," "how should I group these servers," or "recommend device groups for this application." Discovery is read-only and advisory — it observes traffic and recommends a model; it does not create groups.
---

# ExtraHop Application Discovery

Discovers enterprise applications from **wire data** — the traffic the ExtraHop
sensor observes passively at L2–L7 — and recommends how to model them in RevealX
as device groups and tags. Works through the `extrahop_*` MCP tools.

Tools are named with the `extrahop_` prefix below (e.g. `extrahop_search_devices`).
If your client namespaces MCP tools by server, prefix accordingly
(e.g. `ServerName:extrahop_search_devices`).

## Reference files

- **`reference/discovery-methodology.md`** — discovery prerequisites (infrastructure
  baseline, L2/L3 gateway-aggregation awareness, decryption verification) and the four
  discovery approaches (VIP mapping, HTTP host/URI clustering, TLS SNI, behavioral
  scan) in full, with the exact tools and record pivots for each. Load whenever
  running a discovery.
- **`reference/vertical-playbooks.md`** — vertical-specific discovery guidance for
  e-commerce/retail, financial services, government, and healthcare. Load when the
  user names an industry or the environment is clearly vertical-specific.
- **`reference/modeling-recommendations.md`** — naming convention, the device-group
  recommendation matrix, tagging strategy, and the security-hygiene findings table.
  Load before presenting modeling recommendations.
- **`reference/output-templates.md`** — the inventory, per-application, modeling, and
  security-findings table formats. Load before emitting findings.

## Scope

Discovery selects an **approach** from the request. If none is named, run a broad
behavioral scan (Approach 4) with opportunistic VIP, HTTP, and TLS discovery.

| Approach | Trigger | What it does |
|---|---|---|
| **VIP / Load Balancer** | "what's behind the VIP / the F5 / the load balancer" | Identify entry points, map front-end VIPs to backend server pools via record pivots |
| **HTTP Host/URI** | "find the web apps," "discover services by URL" | Cluster HTTP traffic by Host header and URI path prefix into application groups |
| **TLS SNI** | "discover services," encrypted environment | Group services by TLS Server Name Indication, observed even without decryption |
| **Behavioral scan** | "what's running," no approach named | Profile protocol activity per server and infer application boundaries from peer communication patterns |

A target scope (subnet/CIDR, role, device group, or device name) narrows the
discovery. A vertical hint (retail, financial, government, healthcare) applies the
matching playbook.

**Companion skills.** This is the application-mapping member of the ExtraHop RevealX
skill bundle.

- For network and service **performance** — whether a discovered application is
  healthy, latency/error/TCP analysis, root-cause of an outage — use the
  `extrahop-health-check` skill. Discovery answers "what is this and how is it wired";
  the health check answers "is it healthy."
- For **security** work — triaging NDR detections, investigating threats — use the
  `extrahop-triage` skill. Discovery naturally surfaces security-hygiene findings
  (expired certs, weak TLS, unexpected lateral movement); when one looks like an
  active threat rather than hygiene, hand off to `extrahop-triage`.
- To **act on** the model this skill recommends — actually creating an Application
  object, or a device group whose definition isn't expressible through the MCP — use
  the `extrahop-rest-api` skill to generate the REST call. This skill recommends; it
  does not create.

## Prerequisites

Required MCP tools: `extrahop_search_devices`, `extrahop_get_device`,
`extrahop_execute_metric_query`, `extrahop_search_metric_catalog`,
`extrahop_search_records`, `extrahop_search_devicegroups`,
`extrahop_list_devices_in_devicegroup`.

For tagging mode: `extrahop_search_devicetags`,
`extrahop_assign_devicetag_to_devices`, `extrahop_unassign_devicetag_from_devices`,
and the tags must pre-exist.

For console deep-links: `extrahop_get_appliance_metadata` supplies the console FQDN
(`display_host` / `external_hostname`) and the appliance UUID (`hostname`). If absent
(older MCP server), omit links rather than guessing.

If a required tool is missing, say so and proceed with what's available. Without
`extrahop_search_records`, stay at the device + metric level and recommend the
operator confirm front-end-to-back-end pool membership in the RevealX UI — record
correlation (Approach 1, Step 3) is unavailable.

## Core Methodology

Full procedure in `reference/discovery-methodology.md`. The shape:

### 1. Establish environment context (prerequisites)

Before discovering specific applications, baseline the environment so conclusions
aren't drawn from incomplete data.

- **Infrastructure baseline.** `extrahop_search_devices` by role
  (`domain_controller`, `dns_server`) to locate the AD/DNS/DHCP services almost every
  application depends on. `extrahop_search_devicegroups` (type `user_created`) to see
  what is already grouped — never recommend a group that duplicates an existing one.
- **L2/L3 awareness.** If `extrahop_search_devices` returns a few `gateway` devices
  with disproportionately high `net:bytes`, that is **gateway aggregation** — many
  servers hidden behind one router MAC. Flag it and recommend L3 / Remote Discovery
  for those subnets rather than reporting one giant "device."
- **Decryption verification.** Before HTTP- or SNI-based discovery, confirm the sensor
  sees the payload. Query both `ssl_server:connected` and `http_server:req` on a
  candidate. Substantial TLS sessions with near-zero HTTP requests means the traffic
  is encrypted and **not decrypted** — fall back to TLS SNI (Approach 3) and
  behavioral analysis (Approach 4), and flag the decryption gap.

### 2. Run the selected approach

Pick the approach from the request (see Scope table). Each is detailed in
`reference/discovery-methodology.md`. In a broad scan, lead with the behavioral
profile and layer in VIP, HTTP, and TLS findings where the data supports them.

### 3. Correlate front-end to back-end

The single step naive discovery misses: client-to-VIP and VIP-to-pool-member are
**two distinct TCP sessions**. To find a pool, search `~http` records where
`clientAddr` = the LB IP and `host` = the application's Host header; the `serverAddr`
values are the backend members. When HTTP is undecrypted, pivot on `~flow` records
from the LB IP and group by port and temporal correlation.

### 4. Recommend a model

Conclude every discovery with concrete modeling recommendations — group name (per the
naming convention), group type, and exact filter criteria — plus any security-hygiene
findings. See `reference/modeling-recommendations.md`. Discovery is **advisory**: do
not create groups or Application objects; present them for the user to implement (via
the RevealX UI or the `extrahop-rest-api` skill).

## Tagging Mode

Activates when the user says "tag the discovered servers," "mark the members," or
passes `--tag`. Lets discovery persist its grouping as device tags the operator can
filter on, matching the tagging pattern in `extrahop-health-check`.

For each application's confirmed member devices:

1. Tags must pre-exist (`extrahop_search_devicetags` to confirm). If a recommended tag
   is missing, report it and skip — do not claim to have created a tag.
2. `extrahop_assign_devicetag_to_devices` to apply the application/tier tag to the
   member OIDs.
3. Report a TAGGING SUMMARY: tags applied, devices tagged, any errors.

Interactive: confirm the tag and member list before applying. Headless/scheduled:
apply per the run's instructions and report what changed. If unclear, treat as
interactive and confirm first.

## Tool Strategy

| Purpose | Tool | Notes |
|---|---|---|
| Find servers by role / IP / activity | `extrahop_search_devices` | LB candidates, fleets by role, subnet via `ipaddr` CIDR, protocol via `activity` |
| Device details | `extrahop_get_device` | Resolve OID → name/role/vendor; read `discovery_id` for record pivots |
| Existing groups | `extrahop_search_devicegroups` | Check before recommending; also yields capture/sensor OIDs |
| Group members | `extrahop_list_devices_in_devicegroup` | Enumerate an existing group's scope |
| Find metric names | `extrahop_search_metric_catalog` | When unsure of an exact `stat_name` |
| Collect metrics | `extrahop_execute_metric_query` | `cycle: "auto"`; `_server`/`_client` suffix at device level; `_detail` categories for Host/method/status-code breakdowns |
| Transaction pivot | `extrahop_search_records` | The front-end→back-end correlation; `~http`, `~ssl`, `~flow`; max 7d |
| Tags | `extrahop_search_devicetags` / `extrahop_assign_devicetag_to_devices` / `extrahop_unassign_devicetag_from_devices` | Tagging mode only |
| Console FQDN + UUID | `extrahop_get_appliance_metadata` | Deep-links; FQDN from `display_host`/`external_hostname`, UUID from `hostname` |

Query patterns:

- **LB detection:** look for devices with both `ssl_server:connected` /
  `http_server:req` (terminating client traffic) **and** `ssl_client:connected` /
  `http_client:req` (initiating backend traffic) — high fan-out both directions.
- **Host/URI breakdown:** `host_http_server_detail` (stat `req`, string key) for top
  Host headers per server; URI sub-grouping comes from `~http` records.
- **TLS service identity:** `ssl_server:version` and `:cipher` topn for the metrics
  view; distinct `serverName` (SNI) from `~ssl` records for the service inventory.
- **Decryption gap:** compare `ssl_server:connected` vs `http_server:req` on the same
  device.

Start broad (roles, existing groups, capture-level activity), then drill into specific
devices and records only where an application boundary is taking shape. Batch
`metric_specs` into single `extrahop_execute_metric_query` calls. `extrahop_search_records`
is expensive and bounded to 7-day retention — use it for the front-end→back-end pivot
and URI sub-grouping, not for broad enumeration.

## Output

See `reference/output-templates.md` for the full spec. Present discovery as Markdown
tables, not a status verdict (this skill maps applications; it does not grade health):

- **Application Inventory** — one row per discovered application: entry point,
  protocols, server count, decryption status.
- **Per-Application Detail** — member servers as entity links, IPs, roles, protocols.
- **Modeling Recommendations** — recommended group name, type, filter criteria,
  rationale.
- **Security Findings** — any hygiene issues surfaced during discovery.

Keep visible prose short; let the tables carry the detail. Lead with the inventory and
a sentence or two of framing.

## Console Deep-Links

When the report names a device or device group and the console FQDN is available, wrap
the identifier in a Markdown link to its RevealX console page at the discovery time
window, so the operator can jump from the inventory to the live view. Device-group
links need only the FQDN; device links also need the appliance UUID. Both come from
`extrahop_get_appliance_metadata` — FQDN from `display_host` (fall back to
`external_hostname`), UUID from `hostname` (the 32-hex value; never use `mgmt_ipaddr`).
If that tool is unavailable and no FQDN was pasted earlier, present plain backticked
identifiers — a correct unlinked report beats a fabricated link. Never fabricate the
FQDN or UUID.

## Principles

1. **Wire data is the ground truth.** Discovery is built on what the sensor observes,
   not on logs or CMDB entries. It can reveal undocumented dependencies and shadow IT
   that self-reported sources miss — but it only sees what crosses the sensor.
2. **Context over data.** An IP is a fact; "the payment server in the PCI zone" is an
   insight. Contextualize every finding with the business function it serves.
3. **Decryption awareness.** Missing HTTP metrics on a TLS-heavy device means the
   traffic is encrypted, not that the device is idle. Verify decryption before
   concluding from the absence of L7 data.
4. **Existing-model awareness.** Check existing device groups before recommending new
   ones. Duplicate models fragment metrics and confuse operators.
5. **Advisory, not destructive.** Discovery recommends a model; it does not create
   groups or Application objects. Acting on the model is the operator's call (UI or
   `extrahop-rest-api`).
6. **Correlate the tiers.** A list of servers is not an application. Map the
   front-end→back-end relationship through record pivots; that wiring is the point.
7. **Progressive depth.** Start broad (roles, activity, existing groups); drill into
   records and per-device metrics only where an application boundary is forming.
8. **Concise.** Let the tables carry the detail. A discovery answer is an inventory
   plus recommendations, not a wall of prose.
9. **Never fabricate.** Report only what the tools return — never invent devices, IPs,
   hostnames, Host headers, SNIs, metric values, or console URLs. If a query is
   truncated or sampled, say so and scope the claim to what was seen. When evidence is
   missing, say discovery is inconclusive for that segment; do not fill the gap with a
   plausible-looking server or dependency.
