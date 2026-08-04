# Vertical-Specific Discovery Playbooks

Enterprise customers operate in diverse verticals. Tailor discovery with
protocol knowledge specific to the industry. Apply the matching playbook when the user
names a vertical or the environment is clearly industry-specific. The tools are the same
`extrahop_*` MCP tools used everywhere; these playbooks tell you *what to look for*.

A note on internal vs. external traffic: the MCP does not expose a network-locality tool,
so distinguish north-south (external client) from east-west (inter-tier) traffic by
inspecting the `clientAddr` / `serverAddr` IPs in `~http` and `~flow` records against the
known RFC 1918 / internal ranges, or by asking the user for their external CIDR. Do not
fabricate a locality classification.

---

## E-Commerce / Retail

- **Transaction chain.** CDN/WAF → Load Balancer → Web tier → App tier → Payment gateway
  → Database. Map the full purchase flow end to end.
- **Discovery markers.** URI patterns `/checkout`, `/payment`, `/cart`, `/api/v1/orders`
  in `~http` records. High-volume HTTP 200/404 on the web tier; elevated server
  processing time on the DB tier.
- **PCI segmentation.** Identify the Cardholder Data Environment by locating the devices
  in the payment flow — typically a dedicated subnet that also talks to external payment
  processors (identifiable via `~ssl` `serverName` to known gateway SNIs). Recommend a
  `PCI-Scope` tag for these.
- **Seasonal patterns.** Retail traffic varies dramatically. When characterizing volume,
  compare to same-day-last-week, not just the prior 24h.

## Financial Services

- **Trading applications.** Identify by custom-port patterns and ultra-low-latency TCP.
  Watch `tcp:rtt` (and setup time) — even 1 ms of added latency is operationally
  significant. Look for high-volume TCP on non-standard ports between trading desks and
  execution systems.
- **Messaging middleware.** IBM MQ and Kafka brokers show up by role and port pattern;
  `~ibmmq_request`/`~ibmmq_response` records confirm MQ. These brokers are the backbone
  tying front-, middle-, and back-office applications together — map what connects to
  them.
- **Authentication dependencies.** Map Kerberos/LDAP flows from every application tier
  back to the domain controllers (use `~kerberos_request`, `~ldap_request` records and
  `kerberos_client` / `ldap_client` metrics). Every app depends on AD; these dependencies
  are essential to the map.
- **Regulatory reporting.** Look for scheduled, high-volume outbound flows to external
  endpoints (`~ssl` SNI to known regulatory domains, or `~flow` to external IPs on a
  cadence).

## Government (Municipal / Public Sector)

- **Citizen portals.** High HTTP volume from external client IPs. Identify by checking
  `clientAddr` in `~http` records against external ranges (the portal serves the public,
  not internal users).
- **GIS / mapping services.** Identifiable by large HTTP response payloads (`rspBytes`
  in `~http` records) between map servers and application tiers; Esri ArcGIS uses
  recognizable URI patterns.
- **Public safety / dispatch.** Often custom UDP protocols on dedicated ports — find via
  `~flow` records with `proto=UDP` on non-standard ports in the dispatch subnet.
- **Inter-agency dependencies.** Government environments have complex cross-department
  dependencies. Map which systems communicate across agency boundaries by correlating
  the source/destination subnets with traffic patterns.

## Healthcare

- **HL7 / FHIR interfaces.** HL7 v2 uses MLLP (Minimal Lower Layer Protocol) — recognizable
  by its TCP port pattern (commonly 2575) and message framing; `~hl7` records confirm it.
  Modern FHIR uses RESTful APIs over TLS — discover via `~http` Host/URI with `/fhir/` or
  `/api/` prefixes.
- **EHR dependencies.** The Electronic Health Record system (Epic, Cerner, …) is the hub;
  map every ancillary system (Lab, Radiology, Pharmacy) that communicates with it via
  `~flow` and protocol records.
- **DICOM / PACS.** Medical imaging flows show large payloads (tens to hundreds of MB per
  transfer) between modalities and PACS servers, usually on port 104 or 4242; `~dicom_request`
  / `~dicom_response` records confirm.
- **Clinical data encryption.** Verify TLS is active on every flow carrying patient data.
  Flag any HL7 or clinical-API traffic over unencrypted connections as a hygiene finding.
