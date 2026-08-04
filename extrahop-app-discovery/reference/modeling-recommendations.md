# Modeling Recommendations

After discovery, recommend how to model the findings in RevealX. **Do not create
groups, tags, or Application objects** — present recommendations for the user to
implement in the RevealX UI, or generate the REST call with the `extrahop-rest-api`
skill. (Tagging mode in `SKILL.md` is the one exception, and only against pre-existing
tags.)

Every discovery concludes with concrete recommendations: group name, type, and exact
filter criteria, plus any security-hygiene findings.

---

## Naming convention

Use a structured standard that supports filtering, automation, and multi-environment
management:

**Pattern:** `[Vertical] - [AppName] - [Tier] - [Environment]`

Examples:

- `FIN - SAP - DB - PROD`
- `RETAIL - MobileAPI - Web - STAGING`
- `GOV - CitizenPortal - App - PROD`
- `HC - EHR - Interface - PROD`

This lets the user filter dashboards, alerts, and reports by any dimension. Ask the user
for their organizational naming standard before recommending specific names; if they
have one, follow it instead.

---

## Device group recommendations

Recommend groups using filter fields the ExtraHop device-group API accepts (the same
fields `extrahop_search_devices` filters on: `ipaddr`, `name`, `role`, `tag`, `activity`,
`vlanid`, etc.).

| Scenario | Group type | Rationale |
|---|---|---|
| Servers identified by IP range / subnet | **Dynamic** — filter `ipaddr` with CIDR | Automatically captures new servers added to the subnet |
| Servers with a consistent naming convention | **Dynamic** — filter `name` with `~` regex | e.g. `name ~ "PAY-.*-PROD"` captures all production payment servers |
| Servers by role + subnet | **Dynamic** — compound `role` + `ipaddr` | e.g. all HTTP servers in `10.20.30.0/24` |
| Servers identified by tag | **Dynamic** — filter `tag` | Requires the tag to be applied to the devices first |
| Fixed critical assets (core DB cluster, AD controllers) | **Static** | Membership rarely changes; manual curation is appropriate |
| Servers behind a gateway (not individually discovered) | **Custom Device** | Define by IP range + ports to track as one logical entity (see L2/L3 note in `discovery-methodology.md`) |

For each recommended group, provide:

- Suggested name (per the naming convention).
- Group type (dynamic / static).
- Exact filter criteria — field, operator, operand.
- Rationale: why this grouping represents an application tier.

**Performance note.** Dynamic groups with elaborate multi-rule filters increase system
processing time. Prefer a single discriminating field (an IP range or a name pattern)
over combining four or five conditions.

To actually create a dynamic group from a complex filter the MCP can't express, generate
the `POST /devicegroups` call with the `extrahop-rest-api` skill.

---

## Application object recommendations

For mission-critical applications where individual device groups aren't enough, recommend
creating an **Application object** in RevealX. Application objects collect cross-protocol
metrics from all participating devices and give an end-to-end view of service health.

Recommend an Application object when:

- The service is load-balanced and VIP health matters more than any single server.
- The application is multi-tier and the user needs the transaction chain from web → app
  → database in one view.
- Business-specific metrics (e.g. "checkout latency by payment type") would benefit from
  trigger-based collection.

Creating Application objects is **out-of-band for this skill** — the MCP exposes no
application tool. Hand the user to the `extrahop-rest-api` skill, which generates the
`POST /applications` call, or have them define it in the RevealX UI.

---

## Tagging strategy

Tags enable cross-functional visibility across security and IT teams. Ask the user for
their organizational tagging standard, then recommend tags such as:

- **Compliance scope:** `PCI-Scope`, `HIPAA-Data`, `SOX-Relevant`
- **Environment:** `PROD`, `STAGING`, `DEV`, `DR`
- **Ownership:** `Owner: TeamName`, `BU: BusinessUnit`
- **Criticality:** `Tier-1`, `Tier-2`, `Tier-3`

When tagging mode is active (see `SKILL.md`), the skill can apply pre-existing tags to
discovered members via `extrahop_assign_devicetag_to_devices`. It never creates tags; if
a recommended tag doesn't exist, report it and recommend the user create it first.

---

## Security hygiene during discovery

Discovery naturally reveals security posture. Report these as informational findings
alongside the inventory. When a finding looks like an active threat rather than hygiene,
hand off to the `extrahop-triage` skill.

| Indicator | How to detect | Security implication |
|---|---|---|
| Expired TLS certificates | `ssl_server:expired_cert` > 0 | Compliance risk, potential service disruption |
| Self-signed certificates | `ssl_server:self_signed` > 0 | May indicate unauthorized services or missing PKI enrollment |
| Weak TLS versions | `~ssl` `version` = SSLv3 / TLSv1 / TLSv1.1, or `ssl_server:version` topn | Vulnerable to known attacks (POODLE, BEAST) |
| Weak cipher suites | `ssl_server:weak_ciphers` > 0, or `~ssl` `cipherSuite` with RC4/DES/NULL | Vulnerable to interception |
| Unencrypted credentials | HTTP Basic Auth over non-TLS, Telnet (`~telnet`, port 23), unencrypted LDAP (port 389 without STARTTLS) | Credentials transmitted in cleartext |
| Atypical lateral movement | Web server with SMB/CIFS to an unexpected share, or RDP/SSH outside its tier (`~flow` records) | Possible compromise or undocumented dependency |
| Data-exfiltration indicators | Large outbound transfers from a DB tier to external IPs (`~flow` `senderAddr`/`receiverAddr`) | Possible data theft |
