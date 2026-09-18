# Output — formats, specs, and the narrative

**Contents:** the four-tier key-agreement framing (below) · format precedence · CSV spec
and canonical record model · HTML spec, token list and two-stage fill · the written
narrative.

Populate every field **only** from collected data. Never fabricate a device, IP, count,
group name, percentage or URL.

The framing rule from `SKILL.md` governs every sentence here: **"PQC observed" / "no PQC
observed"**, never "PQC-ready / not ready" or "capable / incapable". Four tiers on the
**key-agreement axis**, in descending confidence:

1. **PQC observed, standardized** — firm positive on key agreement. ML-KEM (FIPS 203).
   **This proves the key-agreement axis only** — the same host may still authenticate with
   an RSA/ECDSA certificate or serve obsolete protocol versions, both of which the skill
   requires you to report. Say **"standardized PQC key agreement observed,"** not "done":
   "done" declares the whole migration finished on the strength of one axis.
2. **PQC observed, pre-standard** — Kyber-768-draft. A positive *and* an open work item:
   the codepoint is being retired, so this host migrates again.
3. **Advertised PQC, classical negotiated** (Step 5) — a strong signal, not a proven
   refusal: `supported_groups` is an advertisement, not a key share (RFC 8446 §4.2.8), so
   this is "client advertised PQC support, classical was negotiated," a remediation
   *candidate* to confirm out of band. TLS 1.2 sessions never belong here (tier 4/floor).
4. **No PQC observed** — inconclusive; a candidate to investigate, not a gap.

Never collapse 3 into 4, never promote 4 to 3, and **never merge 1 and 2** — see below.

> **These tiers describe the key-agreement axis, and a host can occupy more than one state
> at once.** A device can negotiate both ML-KEM and draft-Kyber (with different clients),
> or negotiate PQC for one client/SNI and classical for another; and key agreement is
> independent of the authentication and protocol-floor axes. A single `pqc_status` value
> cannot carry that — see the CSV note on `pqc_status` below for how to avoid letting one
> positive observation suppress a migration item on another axis.

---

## Format precedence

1. **User named a format** ("CSV", "HTML", "both") → emit that. A **PDF** request means:
   build the HTML, then render it with an available headless renderer (Chrome
   `--headless --print-to-pdf`, WeasyPrint) and deliver both paths. If no renderer is
   available, deliver the HTML and say explicitly it is *print-ready HTML, not a PDF*.
   **Never claim a PDF was produced when only HTML exists.**
2. **Interactive, format unstated** → **ask** (CSV / HTML / both).
3. **Cannot ask** (headless, scheduled, or the user declined to choose) → **CSV.**

CSV is the only default; HTML is never emitted unrequested. Data collection is identical
either way — only the emit step differs.

---

## CSV

One row per assessed server. Filename `tls_pqc_readiness_<YYYY-MM-DD>.csv`.

| Column | Source |
|---|---|
| `ip_address` | `ipaddr4`, else `ipaddr6`, else `display_name` (~15% have no IP) |
| `device_name` | `display_name` |
| `sensors_seen` | Names/ids of sensors that saw this host |
| `total_tls_sessions_30d` | `ssl_server:connected` — **per-sensor max**, not a sum |
| `total_pqc_sessions_30d` | `ssl_server:post_quantum_kex` — same rule |
| `has_mlkem_observed` | Canonical boolean — ML-KEM (FIPS 203 primitive) key agreement seen |
| `has_kyber_draft_observed` | Canonical boolean — pre-standard Kyber-768-draft seen |
| `has_classical_after_pqc_advert` | Canonical boolean — Step 5: a TLS 1.3 client advertised PQC, classical negotiated |
| `has_tls13_observed` | Canonical boolean — any TLS 1.3 session seen; `false` ⇒ the "no TLS 1.3 observed" floor |
| `variant_resolution` | `resolved` / `unresolved` — `unresolved` when `post_quantum_kex > 0` but the group names were empty |
| `pqc_status` | **Derived** summary of the booleans — the single highest-confidence state: `observed_mlkem` / `observed_kyber_draft` / `observed_variant_unresolved` / `advertised_classical_negotiated` / `none_observed`. See the canonical-model note below |
| `pqc_groups` | Named groups, `;`-separated (`PQC-ECDHE-ML-KEM-768-x25519;…`) |
| `tls_versions` | Version breakdown, `;`-separated — flags the TLS-1.2 floor |
| `unique_clients_pqc_observed` | Distinct client `addr` with a PQC group — **lower bound** |
| `unique_clients_with_classical_observation` | Distinct client `addr` observed with a classical group — **lower bound** |

**Column names carry the semantics deliberately.** `unique_clients_pqc_observed` cannot be
mistaken for a census the way `unique_clients_pqc` can. Both client columns are top-N
lower bounds (`reference/metrics.md`) — prefix with `>=` or add a documented note; emit
`unavailable` only when you cannot even bound them.

> **The classical client column counts *observations*, never a set difference.** Derive it
> directly from the classical partition of the single `key_agreement` tset (Step 6) — the
> distinct `addr` values seen with a classical group. **Do not compute it as
> `all_clients − pqc_clients`**: because a client's PQC tuple can be dropped by top-N
> storage while its classical tuple survives, a set difference falsely counts a PQC client
> as classical-only, and the value can be too high *or* too low — so it is not a bound in
> either direction. Named `unique_clients_with_classical_observation`, the direct count is a
> genuine lower bound (a client seen with classical was seen with classical). Never publish
> a set-difference count as a floor, and never label a client "classical-only" from top-N
> data — the word "only" is a completeness claim the datastore cannot support.

**Resolve state once, into the canonical booleans above; project everything else from
them.** The underlying states are **not mutually exclusive**: a host can negotiate ML-KEM
with one client and Kyber-draft with another, or PQC for one SNI/client and classical for
the next, and key agreement is independent of the auth and protocol-floor axes. A lone
status column silently drops the secondary state — e.g. an `observed_mlkem` label hides
that the same host negotiated classical after a PQC advertisement from 30 other clients.
**Do not let one positive observation suppress a migration item.**

`pqc_status` is a **pure projection** of the booleans — the single highest-confidence
state, in this precedence:

1. `has_mlkem_observed` → `observed_mlkem`
2. `has_kyber_draft_observed` → `observed_kyber_draft`
3. PQC observed but `variant_resolution = unresolved` → `observed_variant_unresolved`
4. `has_classical_after_pqc_advert` → `advertised_classical_negotiated`
5. otherwise → `none_observed`

The booleans are the canonical record and **cannot hide a finding**; `pqc_status` exists
only for at-a-glance reading. If you must collapse to a single column instead of carrying
the booleans, use explicit mixed values (`observed_mlkem+kyber_draft`,
`observed_mlkem+advertised_classical_negotiated`) rather than a lone dominant label — but
the boolean form is preferred. Either way, **`pqc_groups` must still list *every* named
group** so the ML-KEM-vs-Kyber coexistence is recoverable from the row, and keep
`sensors_seen` — it is what makes the session numbers defensible.

> **A single `observed` value inverts the report.** `post_quantum_kex` counts pre-standard
> Kyber-768-draft identically to standardized ML-KEM, so collapsing them files future work
> as finished work. Split the status (`observed_mlkem` / `observed_kyber_draft`)
> from the `key_agreement` groups on that host — the scalar alone cannot tell you which.
> Verified live: 218 hosts were `observed`, but the two carrying **95% of the estate's PQC
> volume** were both on Kyber-draft. A `pqc_status` column that says only `observed`
> reports those two as the success story.

> **Write real CSV.** Device names and resolved hosts are admin- and attacker-influenced
> free text containing commas, quotes and occasionally newlines. Use an RFC 4180 writer
> (Python's `csv`), never string concatenation.
>
> **Neutralize spreadsheet formula injection on every non-numeric cell** — not an
> enumerated subset. Any cell beginning with `=`, `+`, `-`, `@`, tab or CR gets a leading
> `'`. This covers `device_name`, `ip_address` when it falls back to a name, `pqc_groups`,
> `client_name`, and `host` values from detail keys, which are DNS-derived and equally
> untrusted.

**Optional `console_url`** — only if the user asked for clickable output; bare URL, no
Markdown, per `console-urls.md`.

**Client CSV (Step 8)** — `client_ip, client_name, sensors_seen,
total_tls_sessions_30d, total_pqc_sessions_30d, pqc_status, pqc_groups`, saved as
`tls_pqc_client_readiness_<YYYY-MM-DD>.csv`. Same RFC 4180 and injection rules.

---

## HTML

Build one self-contained `tls_pqc_readiness_<YYYY-MM-DD>.html` from
`assets/report-template.html`. Sections:

- **Summary strip** — the four `{{STAT_*}}` tiles. Best use: PQC share of sessions ·
  PQC observed (of N) · advertised-PQC/classical-negotiated servers · hosts with no TLS 1.3
  observed.

  > **Never ship a bare "PQC share of sessions" tile.** It is the number a reader trusts
  > most and the one most easily dominated by one host. **Compute the concentration before
  > you publish the share** — what fraction of PQC volume the top 2–3 hosts carry — and if
  > it is lopsided, qualify the tile in the narrative's first sentence rather than leaving
  > the number to speak for itself. Verified live: the tile read **78.6%** while the honest
  > sentence was "78.6%, of which 95% is two lab hosts on a pre-standard draft."
  > Same arithmetic, opposite conclusion.
- **Estate posture** — the Step 2 distribution. This is the lede, not an appendix.
- **Per-server table** — a **reduced view** of the CSV, not a column-for-column copy. The
  bundled template ships **7** columns (`device_name`, `ip_address`, total sessions, PQC
  sessions, TLS versions, `pqc_status` pill, PQC clients) while the CSV defines **10**; the
  template deliberately omits `sensors_seen`, `pqc_groups`, and the classical-clients
  column. Treat the HTML as the at-a-glance summary and the CSV as the full record — **and
  say so in the narrative**, because omitting `sensors_seen` drops the per-sensor
  provenance that makes the session maxima defensible (`SKILL.md`, Step 3). If a reader
  needs `pqc_groups` (the ML-KEM-vs-Kyber split) or sensor provenance in the HTML itself,
  add the `<th>/<td>` pairs and matching `{{COL_n}}` tokens — keeping headers and row cells
  in sync — rather than presenting the 7-column view as the complete inventory.
- **Findings narrative** — below.

**HTML-escape every data-derived string** (`device_name`, `host`, `pqc_groups`):
`&`→`&amp;`, `<`→`&lt;`, `>`→`&gt;`, `"`→`&quot;`. Additionally **strip or encode `-->` and
`{{`/`}}`** in those values — escaping does not neutralize either, and both are live
hazards (see below).

### The complete token list — fill every one

The most likely visible failure of this skill is shipping a report whose title reads
`{{REPORT_TITLE}}`. Fill all of these:

| Token | Value |
|---|---|
| `{{REPORT_TITLE}}` | `TLS Post-Quantum Readiness` |
| `{{REPORT_SUBTITLE}}` | Scope, e.g. `Internal TLS servers · 10.0.0.0/8` |
| `{{REPORT_DATE}}` | Generation date (appears **twice**) |
| `{{REPORT_WINDOW}}` | `Last 30 days` |
| `{{STAT_1..4_NUM}}` / `{{STAT_1..4_LABEL}}` | The four summary tiles |
| `{{TABLE_HEADING}}` | `TLS Server PQC Inventory` |
| `{{COL_1}}`…`{{COL_7}}` | Column headers for the template's **7-column reduced view**, matching the fragment order below. If you add columns for `pqc_groups` / `sensors_seen`, add matching tokens |
| `{{ROWS}}` | Concatenated `<tr>` fragments (Stage 1) |
| `{{NARRATIVE_INTRO}}` | Opening paragraph |
| `{{NARRATIVE_POINTS}}` | Concatenated `<li>` fragments |
| `{{NARRATIVE_CALLOUT}}` | The observation-vs-capability caveat |
| `{{COMPANY_NAME}}` | Customer or org name (appears **twice**) |
| `{{CONFIDENTIALITY}}` | e.g. `Confidential` |

**Final check: grep the output for `{{` and fail if anything remains.** This one grep
catches the entire class.

### Two-stage fill

The template has a single `{{ROWS}}` placeholder, not a per-row set — duplicating a
generic row would give every copy identical values.

1. **Stage 1 — fragments.** Per server, build its `<tr>…</tr>` by inlining that server's
   **already-escaped** values in the template's column order. Same per finding for `<li>`.
   Concatenate into one rows-string and one findings-string.
2. **Stage 2 — one pass.** A **single** substitution over the template: `{{ROWS}}` ←
   rows-string, `{{NARRATIVE_POINTS}}` ← findings-string, every scalar token ← its value.
   One pass means a device literally named `{{STAT_1_NUM}}` cannot be re-interpreted by a
   later replace.

> **Strip *every* HTML comment from the template as the last step of Stage 2 — not just
> "the two big ones."** The template ships several comment blocks (the header brand guide,
> the `<tbody>` row-shape/pill map, the summary-strip and findings notes, the self-contained
> note). None should reach the customer, and the simplest correct rule is a single
> `re.sub(r"<!--.*?-->", "", html, flags=re.S)` *after* the Stage-2 fill — data values have
> already been escaped and had `-->` neutralized by then (below), so nothing in the data can
> resurrect a comment.
>
> Two traps make a partial strip unsafe:
> - **The `<tbody>` comment has no live `{{…}}` tokens, so it survives the `{{` grep** and
>   ships the internal row-shape instructions (including the pill map) silently. Grep the
>   emitted HTML for a known comment phrase as well as for `{{`.
> - **HTML escaping does not neutralize `-->`.** A device named `a-->b` closes a comment
>   early and dumps whatever follows into the rendered page and the PDF. Neutralize `-->`
>   (and `{{`/`}}`) in every data-derived value regardless — the header comment is
>   deliberately written *without* live braces so the Stage-2 pass can't inject `{{ROWS}}`
>   into it, but that protects only that one comment, not the data hazard.

Numeric cells carry `class="num"` (right-aligned, tabular). **Do not put prose there** —
`unavailable` in a numeric column right-aligns as text. Use a `>=` -prefixed number, or
add a `.na` class for the non-numeric case.

For the `pqc_status` cell the pill class must match the row's actual state — never leave a
hard-coded positive class. The template ships **three** pill classes and there are **five**
states: `observed_mlkem` → `pill yes` (`Observed (ML-KEM)`); `observed_kyber_draft` →
`pill warn` labelled to name the draft (e.g. `Observed (pre-standard Kyber)`), **never**
`pill yes` — it is an open work item; `observed_variant_unresolved` → `pill warn`
(`Observed (variant unresolved)`); the Step-5 state → `pill warn` labelled
`Advertised PQC · classical` (not "Declined" — see tier 3); and `none_observed` → `pill no`.
The pill is what a skimming reader actually reads. When a host holds more than one state
(canonical-model note above), the pill shows the **highest-confidence positive** but the
booleans and `pqc_groups` in the CSV must still expose the rest — the pill must never be the
only place a state is recorded. The `.pill.yes` background uses `color-mix()`, which
**WeasyPrint does not support** — but the template already declares a literal tint
(`#e7f3ec`) *before* the `color-mix()` line precisely so a renderer that drops `color-mix()`
keeps the fallback, so no manual edit is needed; just confirm the positive pill renders
with a background in your chosen renderer.

Design for **Letter landscape** print. The 7-column inventory — specifically the nowrap
`pqc_status` pill in column 6, whose widest label is `Observed (ML-KEM + Kyber-draft)` —
does not fit Letter portrait: the pill overruns the PQC-clients column and both become
unreadable. The template's `@page` rule and `.page` max-width (11in) are set for landscape;
if you re-skin to portrait, either shorten the pill labels or the columns will collide.

**Branding.** The bundled template is neutral and self-contained — no dependency. A
customer's colors, font and logo drop in via its `:root` variables. Official ExtraHop
branding is an optional extra available on request, not a requirement.

---

## Narrative

Lead with posture, not with the table.

1. **Estate posture** — the PQC share of sessions, standardized ML-KEM vs pre-standard
   Kyber, the classical remainder (calling out any `RSA-*` key transport separately as the
   worst harvest-now-decrypt-later exposure), and the TLS version floor. **Per sensor**,
   named, when several contributed — and say you did not sum them and why.
2. **Concentration** — immediately after the share, and in the same breath: what fraction
   of the PQC volume the top 2–3 hosts carry, and whether they are standardized. If a
   handful of hosts carry the number, **the concentration is the finding and the share is
   the footnote**, not the other way around. Verified live: two lab hosts on Kyber-draft
   carried 95% of a 78.6% PQC share, so "we are 78.6% post-quantum" and "our PQC is two lab
   boxes on a retiring draft" describe the same data and lead to opposite decisions.
3. **Advertised PQC, classical negotiated** (Step 5) — TLS 1.3 servers where a client
   advertised a PQC group in `supported_groups` and classical was negotiated anyway. **This
   is the top remediation-candidate list**, but state its limit plainly: `supported_groups`
   is an advertisement, not a key share (RFC 8446 §4.2.8), so this is not proof the server
   refused a PQC key — recommend confirming the server's configured groups out of band.
   Rank by distinct clients as well as by sessions (dedup sessions first, `SKILL.md` Step
   5), and include any server that fell outside the inventory scope, flagged as such. **Keep
   TLS 1.2 sessions out of this list entirely** — they belong in the floor bucket below.
4. **No TLS 1.3 observed** — servers with no TLS 1.3 sessions at all. They could not have
   negotiated PQC in the window — a hybrid group needs TLS 1.3 — so this is more actionable
   than "no PQC observed," and often the larger bucket. State it as an *observation*, not a
   verdict: zero observed TLS 1.3 does not prove the server can't speak it (it may have met
   only TLS 1.2 clients), so recommend confirming the configured maximum version out of band
   rather than writing "cannot do PQC." Verified live: 100 servers carrying 26.1M sessions, and it was the virtualization
   estate — so the remediation owner is one platform team, not 100 service owners. Say that.
   **Do not label a host here merely for being majority-TLS 1.2**: a host with any TLS 1.3
   already supports it and may already do PQC — the floor bucket is zero-TLS-1.3 only.
5. **PQC observed** — count and names, **split standardized vs pre-standard**. Firm
   positive for the former; a positive with an open migration for the latter.
6. **No PQC observed** — **candidates to investigate**, not confirmed gaps. Recommend
   confirming configured groups out of band. Worth splitting by protocol floor: the TLS
   1.3-capable subset has no protocol excuse and is the shorter, more actionable list.
7. **Authentication and SSH**, if collected — weak keys (`RSA < 2048`), `weak_ciphers`,
   and SSH `sntrup`/`mlkem` adoption, which is often the best news in the estate.

   > **Quote the group-level `weak_ciphers` figure, not a per-host sum, and say which you
   > used.** The two do not reconcile and the gap is large: verified live, summing one
   > sensor copy per in-scope host gave **77** against the group-level **17,972 / 18,596**.
   > The group covers every member and every per-sensor copy; a per-host pass covers the
   > CIDR-scoped subset through one chosen OID each. Both are defensible, they answer
   > different questions, and presenting the small one as an estate total understates by
   > two orders of magnitude. If you report both, label them.

8. **Scope and limits** — hosts assessed and how they were scoped; that client counts are
   top-N lower bounds; that the Step-5 signal is a `supported_groups` advertisement, not a
   proven key-share refusal; any sensor that returned nothing and why (a headless or
   metrics-disabled sensor is a **role, not a blind spot**); QUIC as an uncovered surface.
   **For any record-derived finding, give distinct sessions scanned against the population
   `total`** (after the cross-sensor dedup, `SKILL.md` Step 5) — "8 servers across all 5,369
   matching records" and "8 in a 300-record sample" are different claims, and only the first
   is a findings list.

State the observation-vs-capability caveat explicitly so no reader over-reads "No" as
"cannot." If the group was external-heavy or the internal scope came out near-empty, say
so and scope the totals to what was assessed.

Keep it concise — the CSV/HTML carries the per-device detail. Stay with what the wire
shows: regulatory timelines (CNSA 2.0), migration-program planning and board-level framing
are out of scope for this skill.
