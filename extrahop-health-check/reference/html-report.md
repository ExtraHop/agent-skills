# HTML Report Mode

An opt-in, branded, self-contained HTML deliverable for a health check — for
leadership readouts, tickets, and PDF export. Produce it only when the user asks
for it; Default-mode chat Markdown remains correct for almost all interactive
checks.

**The HTML report is a branded EXPORT of the Default-mode chat report.** Same
content, same order, same restraint — the chat artifact with a masthead and
print styling wrapped around it. It is not a richer "detailed mode" rendering. It
mirrors the chat report one-to-one:

| Default-mode chat | HTML export |
|---|---|
| `## Health Check: <target>` | masthead title (the `<target>` alone) + status tag |
| `**<Verdict>** · <window> · <scope>` | status tag (verdict + modifier) + meta row (window, scope) |
| one-sentence problem statement | subtitle |
| `**Findings**` bullets | Findings list |
| `**Key insight.** …` | Key insight paragraph |
| `**What to do**` | What to do list (omit when healthy) |
| `**Drill in further**` | Drill in further list |

There is **no** What-Changed table, Root Cause section, Evidence table, Limits
section, HSI figure, or confidence line — Default mode omits all of those, so the
export does too. Do not add them.

Every guardrail in the skill (freshness gate, two-pass classification, evidence
sufficiency, silent-outage check, NEW/CHRONIC, never-fabricate) applies
identically to the assessment behind the report. The HTML is a *presentation* of
a completed Default-mode assessment, never a shortcut around one.

---

## When to produce HTML

Produce the HTML report only for **artifact-oriented** requests — the words
**"HTML," "PDF," "shareable," "deliverable," "one-pager," "export," "for
leadership/execs,"** or the `--report` flag. These name a file to hand off.

The word **"report" alone is NOT an HTML trigger** — it's ambiguous. A bare
"report me a health check" stays in Default mode; "the full report" / "detailed
report" / "structured data" is **Detailed** mode (verbose Markdown), not HTML.
See the "Mode selection" precedence list in `SKILL.md` (first match wins:
HTML → Detailed → Quick-look → Default). If a request combines cues ("detailed
PDF"), the artifact term wins → HTML. When genuinely unsure whether the user
wants a file or richer chat, ask. Otherwise emit Default-mode chat Markdown.

A chat answer may accompany the report, but the HTML is the deliverable when
requested. When you generate HTML, tell the user the file path in chat and give
a one-line verdict summary; don't paste the whole report body into chat.

### Do NOT produce HTML (defer to the Markdown modes)

- **Stale data.** When the freshness gate fails, the report IS the refusal (see
  "Stale Data Handling" in `output-templates.md`). Do not render a branded page
  around a verdict you can't stand behind. Emit the Markdown stale-data refusal.
- **Quick-look** ("tldr" / "is everything okay"). Intentionally minimal — chat only.
- **Insufficient Evidence from low activity.** The next step is "rerun with a
  longer window," not a formal report. Say so in chat.

If the user explicitly asks for an HTML report on a stale or insufficient-evidence
check, produce a page whose verdict word is **Insufficient Evidence**
(`data-sev="info"` on `<body>`) and whose body is the reason plus what to do —
never a fabricated Normal/Warning/Degraded verdict.

---

## Output location and naming

- A single self-contained HTML file at the **workspace root**.
- Named `health-check-<scope-slug>-<YYYYMMDD>.html` — e.g.
  `health-check-web-app-01-20260609.html`,
  `health-check-http-fleet-20260609.html`,
  `health-check-environment-20260609.html`.
- Inline all CSS. **No external assets and no remote requests of any kind** — the
  template embeds the ExtraHop brand fonts (Source Sans 3 + JetBrains Mono, Latin
  subset) as base64 woff2 `@font-face` rules, with system-font fallbacks in the
  stacks, so the file renders in-brand and identically offline, when downloaded,
  and when printed to PDF (US Letter, page breaks planned via `break-inside`).
  Ship the `<style>` block (fonts included) byte-for-byte; never replace the
  embedded fonts with a remote font `<link>`.
- **Keep the source.** The HTML *is* the source. If asked for a PDF, keep the
  HTML/CSS used to build it; don't delete it without asking.

### PDF delivery (when the user asked for a PDF)

An HTML file alone does **not** satisfy a PDF request. After writing the HTML:

1. **Render it to PDF** with whatever headless renderer is available in the
   environment, writing `health-check-<scope-slug>-<YYYYMMDD>.pdf` next to the
   HTML. Try, in order of preference:
   - headless Chrome/Chromium:
     `chrome --headless --disable-gpu --no-pdf-header-footer --print-to-pdf=<out>.pdf file://<abs-path>.html`
     (on macOS the binary is `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`)
   - `weasyprint <in>.html <out>.pdf`
   - Playwright / `wkhtmltopdf` if installed.
2. **Verify the PDF exists and is non-empty** before telling the user it's done;
   give both file paths (PDF = deliverable, HTML = editable source).
3. **No renderer available** (or no shell access in this client): deliver the
   HTML, and say explicitly that it is *print-ready HTML, not a PDF*, with the
   one-step conversion: open it in a browser → Print → "Save as PDF" (the print
   CSS is already Letter-portrait with page-break rules). Never claim a PDF was
   produced when only HTML exists.

---

## Working with the template

The template at `assets/report-template.html` is the Default-mode report as a
worked HTML example. Your job is content, not design.

1. **Copy it byte-for-byte**
   (`cp assets/report-template.html <workspace>/health-check-<slug>-<date>.html`),
   then edit the copy in place. Never re-type, reformat, or minify the file —
   especially the `<style>` block, which ships **unmodified**.
2. **Fill the marked regions.** Each part is delimited by an HTML comment
   (`<!-- FINDINGS ... -->`, etc.). Replace the example text with this check's
   facts — the same sentences you would write in the chat report.
   **Escape every value that comes from telemetry** before inserting it — device
   names, hostnames, SNIs, URIs, finding text, and metric strings are untrusted
   input and may contain `&`, `<`, `>`, `"`, or `'`. In text/element content
   (findings, Key insight, `<span class="id">`, subtitle, meta) escape `&`→`&amp;`,
   `<`→`&lt;`, `>`→`&gt;`. Inside an attribute (an `href`, `title`, `data-*`)
   also escape `"`→`&quot;` and `'`→`&#39;`. For the console-link `href`,
   URL-encode any identifier interpolated into the path/query (e.g. `encodeURIComponent`
   on a hostname or discovery_id) so a stray character can't break out of the URL
   or inject markup. A device literally named `<img src=x onerror=…>` must render
   as text, never execute. When in doubt, escape — double-escaping a plain name is
   harmless; leaving one unescaped is an injection.
3. **Set the severities.** Two independent levels:
   - **Overall verdict** (once): put `data-sev="…"` on the `<body>` tag and the
     **same** value on the masthead `.status-tag`. This is the worst-affected
     category that drove the overall verdict (mapping below).
   - **Per-finding** (each bullet): set each finding's bold verdict word
     `<span class="fv" data-sev="…">` to **that finding's own** severity — a
     Normal finding is `low`, a Warning finding is `medium`, etc. Do **not** copy
     the overall `data-sev` onto every finding, or Normal/Warning findings will
     render in the Degraded color. In a Degraded report the body is `critical`
     but the "Normal — TCP transport" finding on the same page is still `low`.
4. **Duplicate or delete list items** to fit the check — findings bullets, action
   items. Findings sub-bullets (`<ul>` inside a `<li>`) are for per-server
   breakdowns; use them sparingly, as in chat.
5. **Every identifier is an `<span class="id">`** (device, host, IP) — the mono
   styling mirrors the backtick convention in chat. Link devices thoroughly to
   their RevealX console page: the title device, and the first mention of every
   device in each section. See "Console deep-links" below for the exact rule.
6. **Remove ALL worked-example content.** The hosts and numbers are invented
   (`web-app-01`, `db-prod-02`). Never ship any of them.

If a part doesn't apply, delete it — see the per-verdict rules below. Do not add
parts. If you feel the urge to add a table or a section, you're drifting from the
chat artifact; write a clearer sentence instead.

**Design discipline.** The page is deliberately plain: a branded masthead with a
status tag, a findings list, one paragraph, two short lists. No cards, panels,
boxes, tables, meters, icons, badges, timelines, or diagrams. Color appears in
exactly two places — the masthead status tag and each finding's bold verdict word
— and always encodes the verdict.

---

## The six parts (mirror the chat report exactly)

1. **Masthead** — brand. `doc-kind` = `Health Assessment`; title = the `<target>`
   alone (e.g. `web-app-01`, `Environment`, `HTTP Fleet — 19 web servers`) — no
   "Health Check:" prefix, since the doc-kind label sits directly above; a
   **status tag** under the title carrying the verdict + NEW/CHRONIC modifier
   (e.g. `Degraded · New`), colored by `data-sev`; subtitle = the one-sentence
   problem statement (plain English; for a healthy report, the "all within normal
   ranges" sentence); meta row = window, scope, generated, source.
2. **Findings** — the verdict-first bullet list, the core scannable element. Each
   bullet: bold verdict word (colored) + em-dash + italic category + one sentence.
   Cap at 4–6. Include Degraded/Warning always; include Normal only when ruling it
   out is useful. Sub-bullets allowed for per-server detail.
3. **Key insight** — one prose paragraph: what's happening, what was ruled out,
   what's still healthy. Display names, not metric names ("server processing time",
   not `tprocess`). No threshold quotes.
4. **What to do** — operator actions outside chat. **Omit this whole part on a
   healthy (Normal) report**, matching the chat rule. Cap at 3–4.
5. **Drill in further** — paste-back follow-up questions the user can run in chat.
   Cap at 3–4.
6. **Footer** — generator line and scope/target/date.

The verdict, its modifier, the window, and the scope all live in the masthead
(status tag + meta row) — there is no separate verdict line. Don't restate them
below the masthead.

| Verdict | `data-sev` |
|---|---|
| Degraded | `critical` (multi-category / high impact) or `high` (single localized category) |
| Warning | `medium` |
| Normal | `low` |
| Insufficient Evidence | `info` |

Set the `<body>` `data-sev` from the worst-affected category that drove the
overall verdict. Each finding's `.fv` span carries its own `data-sev`.

### What is deliberately absent

Default mode does not display HSI, confidence lines, a scope/time/HSI block, a
"what changed" table, or a YAML footer — so neither does this export. HSI and
confidence stay internal, exactly as in chat. Don't surface them.

---

## Healthy, Insufficient-Evidence, and quick-look

- **Healthy (Normal).** Render masthead (status tag reads `Normal`) + Findings
  (the Normal categories you're affirming) + Key insight. **Omit "What to do."**
  Keep "Drill in further" if there are useful next checks.
- **Insufficient Evidence / stale data / quick-look.** Prefer to stay in chat
  (see "When to produce HTML"). If the user explicitly wants HTML for an
  Insufficient-Evidence result, set `data-sev="info"`, put the reason in the
  subtitle and Key insight, and give the "what to do / rerun" next steps — never
  a fabricated verdict.

---

## Scope-specific notes

- **Device scope** — the worked example. Title is the device; findings are its
  per-category verdicts; the multi-tier cause lives in Key insight, as in chat.
- **Environment scope** — title `Environment` (the target alone, no "Health
  Check:" prefix — the `doc-kind` label already reads "Health Assessment" above
  it); findings are per-protocol across sensors; name sensors/devices in the
  bullets and Key insight.
- **Protocol-fleet scope** — title names the fleet (`HTTP Fleet — 19 web
  servers`). When the fleet is **bimodal** (see "Bimodal Fleet Presentation" in
  `output-templates.md`), lead the subtitle and Key insight with the shape
  ("12 healthy + 3 degraded"), not an average, and keep NEW findings separate
  from CHRONIC performance-debt findings — using a synthetic *Performance debt*
  category bullet, exactly as the chat report does.

---

## Console deep-links

Link devices thoroughly — this is a launchpad, and a report where the operator
can click a device to land on the right console page beats one where they have to
navigate by hand. See `console-urls.md` for URL syntax, the
`extrahop_get_appliance_metadata` field mapping (FQDN from `display_host`,
appliance UUID from `hostname`), the discovery_id source, and the protocol-slug
table.

**What to link.** Every device and device group that appears as an identifier:

- The **title** device (link it to its `/overview`).
- The **first mention of each device in each section** — Findings, Key insight,
  What to do, Drill in further. Re-linking across sections is intended: each
  section is a skim-point, and the reader may jump straight to one. (Within a
  single section, link only the first mention of a given device; later mentions
  in that same section stay plain.)
- Point each link at the **protocol page the finding is about** — `http-server`,
  `db-server`, `tcp`, `dns-server`, etc. — or `/overview` when the mention is
  general or spans protocols. Match the URL's time window to the assessment
  window.

**What NOT to link.** Paste-back chat prompts that don't name a navigable device;
raw IPs or hostnames that aren't discovered devices; a device whose
`discovery_id` you don't have.

In HTML, wrap the `<span class="id">` in an anchor:
`<a href="https://<fqdn>/extrahop/#/metrics/devices/<uuid>.<discovery_id>/<slug>?from=1&interval_type=HR&until=0"><span class="id">web-app-01</span></a>`.
Masthead links (the title) are styled to stay white with a soft underline; body
links use the accent color — both are handled by the template CSS, so just wrap
the identifier.

**If the FQDN or UUID is unavailable, do not fabricate a link** — leave the
identifier as a plain `<span class="id">`. A correct unlinked report beats a
wrong-linked one. When it's available, though, link every device: sparse linking
is the most common defect in generated reports.

---

## Never fabricate

Report only what the tools returned. Never invent devices, IPs, hostnames, metric
values, percentages, baselines, timestamps, or console URLs. If a query was
truncated or sampled, say so and scope the claim. When evidence is missing, the
verdict is Insufficient Evidence — do not fill the gap with a plausible-looking
number. A branded page makes fabricated telemetry look *more* authoritative, so
the bar here is higher, not lower.

---

## Done criteria

- The report exists as an HTML file at the workspace root, copied from the
  template, with its `<style>` block identical to the template's.
- Its content matches what the Default-mode chat report would say for this check —
  same verdict, same findings, same Key insight, same next steps.
- A reader can state the verdict, target, and window from the masthead alone (the
  status tag carries the verdict + modifier; the meta row carries window + scope).
- Findings are verdict-first, 4–6 bullets, identifiers in `<span class="id">`.
- "What to do" is omitted on healthy reports.
- No table, Root Cause, Evidence, Limits, HSI, or confidence content was added.
- The title device is linked, and every device is console-linked on its first
  mention in each section — or all left plain when the FQDN/UUID is unavailable.
  Never fabricated.
- No placeholder/example content from the template remains.
