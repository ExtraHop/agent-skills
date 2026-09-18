# Scoping — enumerating the servers without corrupting the count

Getting from "the estate" to "a list of hosts to report" is where this assessment is most
often wrong, because the two intuitive moves — filter out `remote`, sum the duplicates —
are **both** wrong, and each fails silently. Everything here was verified against a live
26.3 console fronting multiple sensors.

**Contents:** 1 find the candidates · 2 scope "internal" by CIDR (not `device_class`) and
exclude L2 aggregates · 3 per-sensor copies — never sum · 4 if the group is absent ·
5 sanity-check the scope.

---

## 1. Find the candidates

The built-in **"TLS Server Activity"** device group (id `54` on the verified console;
`53` is "TLS Client Activity") is defined by exactly one criterion:

```json
{"field": "activity", "operand": "ssl_server", "operator": "="}
```

That is all it is. It is **not** an internal-only group, and its name implies a curation
that does not exist.

Two ways in, and the second is better for a scoped assessment:

- **`list_devices_in_devicegroup(id = 54, active_from = "-30d", limit = 5000)`** — page
  on `has_more`/`offset` until exhausted. Returns 14 fields only:
  `critical, custom_name, default_name, device_class, display_name, id, ipaddr4,
  ipaddr6, last_seen_time, macaddr, model, on_watchlist, role, vendor`.
  **Note what is absent: `extrahop_id`/`discovery_id` and `is_l3`.**
- **`search_devices(filter: activity = "ssl_server" AND ipaddr = <internal CIDR>)`** —
  the same population, pre-filtered, in one call. Verified: `activity = ssl_server` plus
  `ipaddr = 10.0.0.0/8` returned 1,199 devices with `has_more: false`.

Use `activity = "ssl_server"` — **not** `extrahop.device.ssl_server`, which is rejected
with `"The specified activity type is invalid."` `device_class` / `devclass` / `is_l3`
are **not** valid `search_devices` filter fields, despite `devclass` appearing in some
tool descriptions.

---

## 2. Scope "internal" with a CIDR, never with `device_class`

**The trap:** the group is majority `device_class: "remote"` (923 of 1,256), which reads
like "external" and is not. `remote` means *Remote L3 discovery* — an IP observed without
associated ARP/NDP, i.e. off-segment. Administrators configure which ranges are remote.

**Verified: 920 of those 923 `remote` devices were RFC1918.** Discarding `remote` throws
away nearly every internal server the assessment exists to find. `device_class` is also
documented as *not identity-stable across sensors*, so it cannot anchor a merge either.

**Instead:**

1. **Enumerate the whole activity population first, *then* classify — do not filter with a
   CIDR predicate up front.** A `search_devices(... AND ipaddr = <CIDR>)` predicate can only
   match a device that *has* an IP, so it silently drops the ~15% of members with no
   `ipaddr4`/`ipaddr6` (below) **before** you ever get to the display-name fallback. Get the
   full membership with `list_devices_in_devicegroup(id = 54, active_from = "-30d")` (or
   `search_devices(activity = "ssl_server")` with no locality clause), then partition it in
   code.
2. **Read the operator's own definition of "internal" first.** `GET /networklocalities`
   returns their CIDR-to-locality map — `networks[]`, an `external` boolean, a name. The
   deployment's definition beats an RFC1918 guess.
3. **Classify each IP-bearing device by locality** against that map (or the internal CIDRs,
   `ipaddr` being CIDR-aware). **Keep the no-IP devices in an explicit `scope_unknown`
   bucket** rather than dropping them — resolve them by another reliable property
   (`macaddr`, MAC-derived `extrahop_id`, resolved `host`) where you can, and report the
   residue as assessed-but-unlocalized so a real internal server without an IP is never
   silently absent from the inventory.
4. **Then exclude the aggregates** — see below. This is the part a CIDR filter cannot do.

If you *do* use the one-shot `activity = "ssl_server" AND ipaddr = <CIDR>` search for
speed, treat its result as the IP-bearing subset only, and reconcile the count against the
full group membership so the no-IP hosts it excluded are visible as a known gap, not a
silent one.

### Exclude L2 aggregates, or they top the report

Three classes appear in the group: `remote` (923), `node` (321), **`gateway` (12)**.

Drop `gateway`, and drop anything that is `is_l3: false` **with no IP**. Verified case:

| Field | Value |
|---|---|
| `display_name` | `HSRP Router 004` |
| `device_class` | `gateway` |
| `ipaddr4` / `ipaddr6` | *empty* |
| `macaddr` | `00:00:0C:9F:F0:04` (HSRP virtual MAC) |
| `ssl_server:post_quantum_kex` | 1,405,152 |

This device is a **MAC-keyed aggregate of traffic routed through an HSRP virtual
router**. It terminates no TLS. Left in, it becomes the highest-volume row in the
inventory, renders with a blank IP, and double-counts the sessions of the real server
behind it. It also defeats a MAC-based merge: its MAC group has no `is_l3: true` member,
so a rule like "keep the L3 twin" leaves it in place.

Also verify how `device_class: "custom"` behaves before trusting it — user-defined
aggregate devices double-count by construction. It could not be enumerated here
(`device_class` is not a searchable field), so treat it as must-check, not as known.

### Expect missing IPs, and do not treat it as an edge case

**49 of 321 `node` devices (15%) had both `ipaddr4` and `ipaddr6` empty.** The
`ip_address` column will be name-only for roughly a sixth of the report. Fall back to
`display_name` (never blank), and do not design the output as if IP is always present.

**This is exactly why the enumeration above must not lead with a CIDR predicate:** a
`ipaddr = <CIDR>` filter cannot match an empty-IP device, so these ~15% never even reach
the fallback — they vanish from the population silently. Enumerate the full membership,
classify IP-bearing devices by locality, and carry the no-IP ones in the `scope_unknown`
bucket (step 1 above) until another property resolves them.

---

## 3. The same host appears once per sensor — and you must not sum

On a console, each sensor independently discovers a host and assigns it a **distinct
OID**. Each OID returns only that sensor's view.

**The critical error is summing them.** Whether the feeds overlap is *not observable from
the metric response*, and when they overlap the sum is inflated — up to N× for N sensors.

### The proof

`HSRP Router 004`, one host, two OIDs sharing `extrahop_id 00000c9ff0040000`:

| OID | node | `connected` | `post_quantum_kex` |
|---|---|---|---|
| 4294967748 | 1 | 1,430,114 | 1,425,146 |
| 8589935127 | 2 | 1,410,936 | 1,405,152 |

Not disjoint halves — **the same sessions seen twice.** The detail lists return the *same
client IPs* with near-identical values (`10.4.1.78`: 1,430,083 vs 1,410,909; `10.4.1.83`:
2 vs 2). Summing reports 2,841,050 sessions where the truth is ~1.42M: a **2× overstatement.**

Independently confirmed at the record layer: `~ssl_open` for one server returned 100
records from 2 appliances that resolved to exactly **50 distinct `(flowId, clientPort)`
sessions, all 50 seen by both.** The duplication is real, not a metric artifact.

**And the overlap is not consistent.** `kvm-lab-1` (`extrahop_id 549f351b66b00000`)
returned 51,145,160 on node 2 but 7,164,090 on node 1 — *partial* overlap. So neither
`sum` nor `max` is universally correct, and nothing in the response distinguishes the
cases.

### What to do instead

- **Default: report the per-OID maximum** as a conservative floor, and **name the sensors
  that saw the host.** A floor you can defend beats a total you cannot.
- **Better, when it matters: test for overlap.** Pull the per-OID *detail* client sets. If
  the key sets substantially intersect, the OIDs are duplicate views → take the **max per
  peer key**. Only sum when the key sets are genuinely disjoint.
- **Client sets: always union by `addr`.** Union is correct either way and unaffected by
  overlap.
- **Never drop an OID for being empty.** A per-sensor copy is often empty while its
  sibling carries the sessions. Judge the host, not the OID.
- **If you fold two device records into one host, union both of their client sets** into
  the survivor. Discarding a record wholesale silently drops clients seen only by it.

### Grouping the copies cheaply

`extrahop_id` and `is_l3` are **not** in the device-list response — only `get_device`
returns them, one call per device. Keying a merge on them therefore costs one call per
device (333 on this small console, thousands on a real one). Do not pay that blindly.

Two free substitutes:

- **`node_id = OID >> 32`** — exact, arithmetic, zero calls. Verified:
  `25769803778 >> 32 = 6`, matching `node_id: 6`. (This is the full node id, not merely a
  "node 1 vs node ≥ 2" split.)
- **`macaddr`** — present for every device sampled (0 of 1,256 had an empty MAC), and
  `extrahop_id` is MAC-derived, so MAC grouping is an equivalent free proxy.

**Verified shortcut:** all 152 multi-OID internal MAC groups were exactly size 2 with
`node_id` pattern `(1, 2)`, and no MAC group had differing IPs. So: **group by `macaddr`;
where members differ only in `OID >> 32`, they are per-sensor copies of one host.**
Reserve `get_device` for the ambiguous residue — and when you do call it, **cache
`discovery_id` from the same response** for console deep-links rather than fetching twice.

**Never dedupe on IP.** DHCP, NAT and VIP failover recycle addresses within a 30-day
window, so IP-merging fuses genuinely different hosts.

If a MAC group has more than one `is_l3: true` member, keep the one with the highest
`connected` and say you did.

---

## 4. If the group does not exist

Older firmware may lack it. `search_devices(filter: activity = "ssl_server")` is the
direct equivalent of the group's own definition and is the right fallback — verified
working.

Do **not** fall back to "query `ssl_server:connected` across all known devices":
`query_metrics` requires an explicit `object_ids` array, so that phrasing hides a full
paginated enumeration plus chunking under the 5000-cell cap — ~500 metric calls on a
50k-device estate.

---

## 5. Sanity-check the scope before reporting

- If almost nothing internal remains after filtering, **say so.** The console likely sees
  mostly north-south traffic, and server-side readiness is best assessed where the
  internal servers are.
- Cross-check the assessed host count against Step 2's estate totals. If the per-host
  sessions sum to far less than the group total, hosts are missing from the enumeration —
  not from the estate.
