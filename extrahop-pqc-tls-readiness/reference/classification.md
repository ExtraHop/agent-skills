# Classification — what counts as post-quantum, and what counts as weak

Verified against the live metric catalog and live records on firmware **26.3**.

**Contents:** TLS classification (the `PQC-` prefix rule; RSA key transport) · the protocol
floor · authentication proxies · SSH name-based classification · `~ssl_open` records and the
PQC codepoints.

---

## TLS: trust the counter, classify by prefix

ExtraHop increments `post_quantum_kex` whenever the negotiated key-agreement group is a
recognized PQC or hybrid group. **Do not maintain your own allow-list** — use the counter
for counts, and the **`PQC-` prefix** (case-insensitive) when you need to classify a named
group from `key_agreement`.

Group names observed live on this estate:

| Group name | Type |
|---|---|
| `PQC-ECDHE-ML-KEM-768-x25519` | Hybrid X25519 + ML-KEM-768 — **FIPS 203, standardized** |
| `PQC-ECDHE-Kyber-768-x25519` | Hybrid X25519 + Kyber-768 — **pre-standard draft** |
| `ECDHE-x25519`, `ECDHE-secp256r1`, `ECDHE-secp384r1`, `ECDHE-secp521r1` | Classical ECDHE |
| `ECDHE-curveSM2`, `ECDHE-NONSTANDARD` | Classical, non-standard curve |
| `DHE-2048` | Classical finite-field DH |
| `RSA-2048`, `RSA-4096` | **RSA key transport — not forward-secret** |

Suffixes vary by firmware and by what clients offer, so **match the prefix, not a fixed
list.**

**Separate ML-KEM from Kyber in the report.** They are not interchangeable: ML-KEM is the
FIPS 203 standard, Kyber-768-draft is a pre-standard experiment that will need migrating
*again*. On this estate the pre-standard variant carried several times the volume of the
standardized one — that is a finding, not a footnote.

### RSA key transport deserves its own callout

`RSA-*` in `key_agreement` is not ECDHE-with-an-RSA-cert; it is **RSA key transport**,
where the session key is encrypted to the server's public key. It has **no forward
secrecy**, so a harvested session is decryptable the moment the key is recovered. It is
the single worst harvest-now-decrypt-later exposure in a TLS inventory and should be
called out separately from "classical ECDHE".

---

## The protocol floor: a TLS 1.2 session is a structural blocker (a mixed-version host is not)

**Hybrid PQC groups exist only in TLS 1.3.** A TLS 1.2 *session* cannot negotiate one.

So a server that shows **no `TLSv1.3` sessions at all** did not — and in this window could
not have — negotiated PQC: a hybrid group needs TLS 1.3. That is a concrete, actionable
finding, and it is one stat away from the key-agreement query. **But keep it on the
observation axis.** Absence of TLS 1.3 *on the wire* is not proof the server cannot speak
it — a TLS 1.3-capable server that met only TLS 1.2 clients in the window shows zero TLS
1.3 too. So report the host as **"no TLS 1.3 observed"**, never "cannot do PQC," and for the
ones that matter confirm the server's configured maximum protocol version out of band
before calling it a hard blocker. This is the same observation-≠-capability rule the rest
of the skill runs on; the "cannot" is a property of the TLS 1.2 *session*, not a proven
property of the *host*.

**But be careful promoting a version *mix* to a capability claim.** A host that is majority
`TLSv1.2` yet carries even a handful of `TLSv1.3` sessions already supports 1.3 and may
already negotiate PQC — the breakdown counts sessions and peer behavior, not the server's
capability ceiling. Classify each TLS 1.2 *session* as structurally ineligible, but label a
*host* only as **"no TLS 1.3 observed"** unless its TLS 1.3 count is genuinely zero. A host
with `post_quantum_kex > 0` obviously supports 1.3 no matter how much TLS 1.2 it also
serves — never let a majority-1.2 mix classify a PQC-observed host as unable to do PQC.

Versions observed live, including ones that are findings in themselves:
`TLSv1.3`, `TLSv1.2`, **`TLSv1.0`** (268 sessions), `TLSv1.3-draft-26-fb`.

---

## Authentication: proxies only, and say so

Every RSA and ECDSA certificate in the estate is quantum-vulnerable, and certificate
rotation is the long-lead item in any migration. But **there is no certificate
signature-algorithm metric.** The closest proxies:

| Signal | Stat | Key type |
|---|---|---|
| Key size | `ssl_server:keysize` | **`intval`** — read `key.intval`, not `key.str` |
| Public-key curve | `ssl_server:cert_pubkey_curve` | string |
| Cert identity / expiry | `ssl_server_detail:cert_subject`, `cert_expiration`, `cert_not_before` | string |

Key sizes observed live: `1024` (61 sessions — **an RSA-1024 certificate still in
service**), `2048`, `3072`, `4096`, and `256`/`384` for EC keys.

**Interpreting `keysize`:** small values (`256`, `384`, `521`) are EC key sizes and are
normal; large values (`1024`–`4096`) are RSA moduli. Correlate with
`cert_pubkey_curve` — a session with a curve name is EC-authenticated.

Flag as findings: **RSA < 2048** (weak today, independent of quantum), `DHE-1024` or
smaller, and `weak_ciphers > 0`. State plainly that the full authentication story requires
`~ssl_open` records or an out-of-band certificate inventory — do not imply metrics cover it.

---

## SSH: name-based classification is mandatory

**There is no `post_quantum_kex` counter for SSH** — confirmed by catalog search. Classify
`ssh_server:kex_algorithm` / `ssh_client:kex_algorithm` by name prefix:

| Prefix | Post-quantum? | Notes |
|---|---|---|
| `sntrup*` | **Yes** | Streamlined NTRU Prime, hybrid with X25519. e.g. `sntrup761x25519-sha512@openssh.com` |
| `mlkem*` | **Yes** | ML-KEM, OpenSSH 10.0+. e.g. `mlkem768x25519-sha256` |
| `curve25519-*` | No | Classical, incl. `curve25519-sha256@libssh.org` |
| `ecdh-sha2-*` | No | Classical ECDH |
| `diffie-hellman-*` | No | Classical DH; `*-sha1` and `*-group1-*` are weak outright |

Both `@openssh.com`-suffixed and bare forms occur for the same algorithm — **match the
prefix and normalize**, or you will report one algorithm as two.

Live on this estate (sensor 2, 30 days): `sntrup761x25519-sha512@openssh.com` 192,475 ·
`curve25519-sha256@libssh.org` 75,882 · `curve25519-sha256` 2,346 ·
`ecdh-sha2-nistp256` 253 · `mlkem768x25519-sha256` 174 · `sntrup761x25519-sha512` 10.

SSH is often the **best** PQC news in an estate — OpenSSH enabled `sntrup` by default long
before TLS stacks shipped ML-KEM — so it is worth reporting even when TLS looks poor.

---

## `~ssl_open` records: the capability gap

Metrics record only what was **negotiated**. Records additionally carry what the client
**offered**, which is the only way to distinguish "the server declined PQC" from "no
client ever asked."

| Field | Type | Meaning |
|---|---|---|
| `isPostQuantumKeyAgreement` | boolean | The session used a PQC key agreement |
| `keyAgreement` | string | The negotiated group, e.g. `PQC-ECDHE-ML-KEM-768-x25519` |
| `supportedGroupsHex` | string | **The client's offer** — concatenated 4-hex codepoints |
| `version` / `encryptionProtocol` | string | `TLSv1.3`, `TLSv1.2`, … |
| `cipherSuite`, `cipherSuitesHex` | string | Negotiated suite; client's offered list |
| `certificateKeySize`, `certificatePublicKeyType`, `certificateSignatureAlgorithm` | | **The real signature algorithm** — not available as a metric |
| `serverIsExternal`, `clientIsExternal` | boolean | Scope filters that beat a CIDR guess |
| `ja4Fingerprint`, `ja4Server` | string | Client/server stack fingerprints |

### PQC codepoints in `supportedGroupsHex`

**Do not treat any fixed list — including this one — as the complete PQC offer surface.**
The [IANA TLS Supported Groups registry](https://www.iana.org/assignments/tls-parameters/tls-parameters.xhtml)
is the authority and it grows; derive the current set from it before scanning — **every**
ML-KEM group (the hybrid `*MLKEM*` codepoints *and* the pure `MLKEM*` ones) plus the
retiring Kyber-draft groups. The codepoints registered as of this writing (verify against
the live registry):

| Codepoint | Group | Notes |
|---|---|---|
| `11ec` | `X25519MLKEM768` | ML-KEM (FIPS 203 primitive) — the dominant real-world offer; the only hybrid IANA marks "Recommended" |
| `11eb` | `SecP256r1MLKEM768` | ML-KEM (FIPS 203 primitive) |
| `11ed` | `SecP384r1MLKEM1024` | ML-KEM (FIPS 203 primitive) |
| `11e9` | `SecP256r1MLKEM512` | ML-KEM-512 hybrid (early draft) |
| `11ea` | `MLKEM512X25519` | ML-KEM-512 hybrid (early draft) |
| `11ee` | `curveSM2MLKEM768` | ML-KEM + SM2 hybrid (draft) |
| `0200` / `0201` / `0202` | `MLKEM512` / `MLKEM768` / `MLKEM1024` | **pure** ML-KEM, no ECDHE hybrid (draft) |
| `6399` | `X25519Kyber768Draft00` | pre-standard Kyber draft — **now OBSOLETE** (obsoleted by the ML-KEM hybrids) |
| `639a` | `SecP256r1Kyber768Draft00` | pre-standard Kyber draft — **now OBSOLETE** |

`11eb`/`11ec`/`11ed` are the standardized ML-KEM key-agreement groups; `11ec` is the one
you will actually see. The pure-ML-KEM (`0200`–`0202`) and ML-KEM-512 (`11e9`/`11ea`)
codepoints are rare in the wild today, but they belong in the scan so that a future client
offering one is not silently missed — the cost of an extra codepoint in the loop is one
query. Treat the five originally-verified codepoints (`11ec`/`11eb`/`11ed`/`6399`/`639a`)
as the *verified-on-26.3* subset, **not** as the whole surface.

Non-PQC codepoints you will see alongside: `001d` (X25519), `0017` (secp256r1), `0018`
(secp384r1), `0019` (secp521r1), `001e` (X448), `0100`/`0101` (FFDHE).

> **A codepoint search over this field is a substring match and produces false
> positives.** `supportedGroupsHex` is a *concatenation* of 4-hex codepoints with no
> delimiter, so `~ "11ec"` also matches a boundary spanning two unrelated ones — the
> trailing `11` of one and the leading `ec` of the next. **Split every returned value into
> 4-character-aligned pairs and confirm the codepoint sits on an alignment boundary**;
> discard the record otherwise. Verified real value, where the match *is* aligned and
> genuine: `11ec001d0017001e0018001901000101`.
>
> Only a client-side re-parse can tell the two cases apart, so the filter narrows the
> population and the parse decides the finding. Never report a raw filter hit count as a
> decline count.

Note `11ec` also appears as a **GREASE-adjacent-looking** leading value in real client
offers — it is genuine; verified paired with `isPostQuantumKeyAgreement: true` on
negotiated sessions.

On this estate, querying this set over 6 hours returned `11ec` = 5,369 records and **every
other codepoint = 0**. That zero is why the loop matters: a single-codepoint query that
happens to pick one of the empty ones reports a clean estate.

### Require `keyAgreement exists`, or you will invent findings

A record where the client advertised a PQC codepoint but `isPostQuantumKeyAgreement` is
`false` is a **candidate** — "client advertised PQC, classical negotiated" — *only if a
ServerHello was actually observed*, and it is **not** a proven decline (see the key_share
and TLS-1.2 caveats below).

**Verified: 11 of 200 records had no `keyAgreement` and no `cipherSuite` at all** — the
server side of the handshake was not captured (their `ja4Server` is the empty-string
hash `e3b0c44298fc`). Those are truncated captures, not findings. Counting them
manufactures findings against innocent servers.

Always filter on `keyAgreement exists`, and to `version = "TLSv1.3"`. Verified live over
the **complete** 6-hour population (5,369 records, cursored, not sampled, deduplicated
across sensors): **8** distinct internal servers negotiated `ECDHE-x25519` or
`ECDHE-secp256r1` after a client advertised `X25519MLKEM768` — four of them `TLSv1.3` (the
candidates worth investigating) and the remainder `TLSv1.2`, where the protocol forbade a
hybrid group and the "decline" is a mirage.

> **`supported_groups` is an advertisement, not a key share.** RFC 8446 §4.2.8 lets a TLS
> 1.3 `ClientHello` carry ML-KEM in `supported_groups` while its `key_share` holds only
> X25519; the server then selects X25519 without rejecting PQC and without a
> HelloRetryRequest. **The record exposes the advertised groups (`supportedGroupsHex`) and
> the extension *types* present (`clientExtensionsHex`) but neither the `key_share` group
> contents nor an HRR flag** — verified live on 26.3. So a low `isPostQuantumKeyAgreement`
> against a PQC advertisement is a *weaker* signal than "the server refused a PQC key": it
> is "advertised, not negotiated." A definitive decline would need an observed PQC
> `key_share` or an HRR, and the record does not carry either today.

Two things that population size teaches, both of which a `limit`-capped query hides:

- **Rank by sessions and by distinct clients, separately.** The widest client exposure
  here (`ldap-01.internal.example.com`, 26 distinct clients) was only the *third* largest
  by session count. Session volume answers "how much traffic is exposed"; client count
  answers "how many peers are being downgraded" — and the second is the better proxy for
  blast radius. Dedup sessions across sensors before either ranking.
- **A candidate need not be in your inventory.** Records are scoped by `serverIsExternal`,
  the inventory by group membership, so the two populations differ. That same
  `ldap-01.internal.example.com` was not a member of `TLS Server Activity` at all. Report it
  anyway, flagged as outside the inventory scope (`SKILL.md`, Step 5).

### Cost

Records are retention-bounded and far heavier than metrics. Scope the capability-gap query
to a **short window** (hours) and use it to *qualify* the metric-derived inventory, not to
build it. `~quic_open` exists separately — **PQC in TLS-over-QUIC is invisible to
`ssl_server` metrics**, so note QUIC as an uncovered surface rather than assuming zero.
