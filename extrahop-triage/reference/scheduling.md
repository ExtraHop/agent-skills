# Scheduling Detection Triage

The triage logic is the same regardless of how it's invoked — only the
scheduling mechanism differs by client. This mirrors the structure of the
companion `extrahop-health-check` skill's scheduling guide so the bundle behaves
consistently whether it's screening network health or SOC detections.

## What scheduled triage is for

The common enterprise SOC pattern: a recurring unattended pass that clears
high-confidence noise from the queue and surfaces the rest for a human, so the
day-shift analyst starts with a smaller, prioritized queue instead of an
overnight backlog.

| Cadence | Goal | Window |
|---|---|---|
| Every morning (start of shift) | Triage overnight detections; auto-close high-confidence noise; leave a prioritized escalation queue | last 12–24h |
| Hourly / every few hours | Keep a busy queue from piling up between shifts | last 1–4h |
| After a known event (scan window, pen test, maintenance) | Clear the expected benign burst | the event window |
| Weekly (AI accuracy review) | Score prior AI dispositions against human outcomes; report agreement/disagreement and tuning candidates | last 7–30d |

## Headless behavior contract

A scheduled run has no human in the loop, so the interactive "confirm before
each state change" step does not apply the same way. Instead, follow the headless
rules from `SKILL.md`:

- **Auto-close only what is safely closable.** Close only **High-confidence**
  false positives or benign true positives, always with
  `resolution="no_action_taken"` and `ai_disposition` set to the verdict. This is
  the same eligibility gate as an interactive batch close — the run just supplies
  the one approval implicitly via its instructions.
- **Never auto-open investigations** for anything below a clear-cut,
  High-confidence malicious true positive. Sub-High-confidence true positives and
  undetermined-but-suspicious items go to the escalation queue, classified
  `indeterminate` (or their preliminary disposition), **left open**.
- **Record `ai_disposition` on every detection the run acts on or escalates** —
  closed or escalated. Unattended runs are the primary source of accuracy
  telemetry, so coverage of acted/escalated items matters most here; a verdict
  the run doesn't record can never be scored against the human outcome. The
  disposition write is non-destructive and doesn't depend on the close-
  eligibility gate. (Transient noise the run leaves untouched needs no standalone
  disposition write.)
- **Report exactly what changed.** Emit a run summary listing every detection
  closed (with IDs and the shared verdict/disposition/resolution), the
  still-open escalation queue, and **disposition coverage** (how many of the
  acted/escalated detections carry an `ai_disposition`). This is the unattended
  analogue of the health-check skill's TAGGING SUMMARY.
- **Persist the escalation queue to a file** when the environment has a writable
  filesystem and the queue is non-trivial, so the next interactive session (or
  the day-shift analyst) can pick it up. See
  [escalation.md](escalation.md) for the file contract (`escalation-queue.json`).
- **Never fabricate.** The data-integrity rule holds unattended: report only what
  the tools return; if a run returns nothing, record that and stop.

If a run's instructions are ambiguous about what it may close, default to the
conservative reading — leave detections open and escalate — rather than closing
something that shouldn't be.

## Scheduled AI-accuracy review

A separate, less frequent run (for example weekly) closes the measurement loop:
it scores the AI dispositions recorded by prior triage runs against the human
outcomes those detections later received, and reports where the AI agreed and
disagreed. This run **reads and reports only** — it does not close detections or
open investigations. It follows Step 8 of
[triage-workflow.md](triage-workflow.md): pull a time-scoped population and
filter client-side to those carrying both an `ai_disposition` and a human
outcome, rank the human signal by strength (investigation `assessment` and
`action_taken` are strong; a bare `no_action_taken` close is weak/ambiguous and
excluded from the rate), and emit a grounded summary. **Report the
missed-true-positive count as a separate headline safety metric**, with tuning
candidates. Never fabricate an accuracy rate; report raw counts when the
strong-signal population is too small to be meaningful.

```
/schedule weekly Review AI triage accuracy over the last 7 days: compare each detection's ai_disposition to the human resolution or investigation assessment, and report agreement, disagreement, and tuning candidates. Read-only.
```

## Claude Code (CLI)

### `/loop` — in-session, ephemeral

Best for ad-hoc monitoring during an incident or a change window. Expires after
7 days; requires the session to stay open. Inherits MCP access from the session.

```
/loop 1h Triage new detections from the last hour and close only high-confidence noise; escalate the rest
/loop 4h Triage detections on our critical devices and summarize what needs investigation
```

Stop with `Esc`.

### Cron with `claude --print`

For traditional UNIX scheduling. Requires the `claude` CLI and a project
directory with the ExtraHop RevealX MCP configured.

```bash
# Every weekday at 7am: triage overnight detections, close high-confidence noise
0 7 * * 1-5 cd /path/to/project && claude --print -p "Triage detections from the last 12 hours. Close only high-confidence false positives and benign true positives (no_action_taken). Leave everything else open as a prioritized escalation queue and write it to escalation-queue.json. Report what you closed." --allowedTools "mcp__extrahop__*"

# Hourly: keep the queue trimmed
0 * * * * cd /path/to/project && claude --print -p "Triage new detections from the last hour; close high-confidence noise only; summarize the rest" --allowedTools "mcp__extrahop__*"
```

## Claude Desktop — Routines

1. Routines sidebar → New routine → Local
2. Name: `extrahop-triage`
3. Instructions: `Triage overnight detections, close high-confidence noise, escalate the rest`
4. Schedule: e.g. weekdays at 7:00 AM
5. Working folder: the project directory with the ExtraHop RevealX MCP configured
6. Run once manually to approve permission prompts

Enable "Keep computer awake" for reliability.

## Claude.ai — Cloud Routines

For 24/7 triage without a workstation. Requires Pro, Max, Team, or Enterprise.

**Prerequisite:** the ExtraHop RevealX MCP must be reachable from Anthropic's
cloud — a remote (HTTPS) MCP server or a connector bridging to your on-prem
appliance. Local stdio MCP binaries won't work.

```
/schedule daily at 7am Triage overnight detections, close high-confidence noise, escalate the rest
/schedule every 4 hours Triage detections on our critical devices and summarize what needs investigation
```

Note: a cloud routine has no persistent filesystem, so the escalation queue
stays in-context and in the run summary rather than in `escalation-queue.json`.

## GitHub Copilot / Gemini CLI / generic agents

Same pattern as the health-check skill: no first-class chat scheduler, so drive
the triage prompt from CI cron (GitHub Actions `schedule:`), an OS scheduler, or
a container scheduler (Kubernetes CronJob, systemd timer). Any agent platform
that supports MCP and accepts a text prompt can run scheduled triage; only the
invocation wrapper changes. The MCP server must be configured where the agent
runs, with credentials mounted (never baked into images), and output logged to a
durable location for audit.

## Best practices

- **Match window to cadence.** Hourly runs → 1h window; morning runs → the
  overnight window. Mismatches re-triage the same detections or miss some.
- **Close conservatively unattended.** When in doubt, escalate rather than close.
  An over-eager scheduled close can bury a real threat; a missed close just
  leaves a little noise for the analyst.
- **Always produce a run summary.** A scheduled run nobody can audit is worse
  than none. List what closed and what's still open.
- **Set failure alerting on the scheduler.** If the job stops running, the queue
  silently piles up — you want to know.
- **Pair with health-check scheduling.** SOC triage and NOC health checks can run
  on the same scheduler against the same environment; stagger them so they don't
  contend for the appliance at the top of the hour.
