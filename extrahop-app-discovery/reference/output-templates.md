# Output Templates

Present discovery findings as Markdown tables with a sentence or two of framing. This
skill **maps applications** — it does not grade health, so do not emit a status verdict
(that is `extrahop-health-check`'s job). Keep visible prose short; let the tables carry
the detail.

Identifiers are backticked names/IPs. Never fabricate a server, IP, Host
header, SNI, or link.

---

## Application Inventory (top-level summary)

One row per discovered application:

| Application | Entry Point | Protocols | Server Count | Decryption Status |
|---|---|---|---|---|
| Checkout Service | `10.20.1.100` (VIP) | HTTP, TLS, TCP | 4 backend servers | Decrypted |
| Payment Gateway | `payments.example.com` (SNI) | TLS | 2 servers | Not decrypted |
| … | … | … | … | … |

---

## Per-Application Detail (one table per application)

| Server | IP Address | Role | Protocols | Notes |
|---|---|---|---|---|
| [web-01](device/12345) | `10.20.2.10` | http_server | HTTP, TLS | Primary web tier |
| [web-02](device/12346) | `10.20.2.11` | http_server | HTTP, TLS | Primary web tier |
| [db-01](device/12350) | `10.20.3.5` | db_server | TCP (MySQL) | Database tier |

---

## Modeling Recommendations (per application)

| Recommended Group Name | Type | Filter Criteria | Rationale |
|---|---|---|---|
| RETAIL - Checkout - Web - PROD | Dynamic | `ipaddr = 10.20.2.0/24` AND `role = http_server` | Captures all web servers in the checkout subnet |
| RETAIL - Checkout - DB - PROD | Static | Members: db-01 (OID 12350) | Fixed database cluster |

See `modeling-recommendations.md` for the naming convention and the group-type matrix.
State plainly that these are recommendations for the user to implement (RevealX UI or the
`extrahop-rest-api` skill) — discovery does not create them.

---

## Security Findings (only if any surfaced)

| Finding | Device | Detail | Recommendation |
|---|---|---|---|
| Expired TLS certificate | [web-01](device/12345) | Certificate expired 2026-03-15 | Renew certificate |
| Weak TLS version | [legacy-app](device/12400) | TLS 1.0 in use | Upgrade to TLS 1.2+ |

Omit this table entirely when discovery surfaces no hygiene issues. If a finding looks
like an active threat rather than hygiene, note it and recommend handing off to the
`extrahop-triage` skill.

---

## Tagging Summary (tagging mode only)

When tagging mode applied tags to discovered members, append:

```
TAGGING SUMMARY
- Tag "PCI-Scope" applied to 6 devices: web-01, web-02, app-01, app-02, db-01, db-02
- Tag "RETAIL-Checkout" not found — skipped (recommend creating it first)
- Errors: none
```

Report what was applied, what was skipped (missing tags), and any errors. Never claim to
have created a tag that didn't already exist.

---

## Inconclusive segments

When discovery can't resolve part of the environment — undecrypted traffic with no SNI,
gateway-aggregated subnets, or insufficient records — say so explicitly and scope the
claim to what was observed. For example: "The `10.40.0.0/16` subnet is reached through a
single gateway device (L2 aggregation); individual servers there could not be discovered.
Recommend enabling L3 Discovery for this subnet." Do not fill the gap with a
plausible-looking application.
