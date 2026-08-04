# Scheduling Health Checks

The skill's logic is the same regardless of how it's invoked — only the scheduling mechanism differs by client.

## General Guidance

| Check Type | Interval | Window |
|---|---|---|
| Environment-wide | every 4–24 hours | match interval (4h → `4h`, 24h → `24h`) |
| Critical devices (DCs, core LBs, primary DBs) | every 1–4 hours | `1h` or `4h` |
| Protocol fleet (DNS, HTTP, Kerberos) | weekly, or after changes | `7d` |

Always enable tagging mode for scheduled runs so health state persists between executions and is queryable from the ExtraHop UI.

Scheduled/headless runs apply tag changes without confirmation. Interactive sessions confirm first.

## Claude Code (CLI)

### `/loop` — in-session, ephemeral

Best for ad-hoc monitoring during deployments or change windows. Expires after 7 days; requires the session to remain open. Inherits MCP access from the current session.

```
/loop 1h Run a network health check and tag the results
/loop 4h Check the health of dc-01, web-lb-01, dns-primary and tag the results
```

Stop with `Esc`.

### Cron with `claude --print`

For traditional UNIX scheduling. Requires `claude` CLI and a project directory with MCP configuration.

```bash
# Daily at 8am
0 8 * * * cd /path/to/project && claude --print -p "Run a full environment network health check and tag the results" --allowedTools "mcp__extrahop__*"

# Every 4 hours, critical devices
0 */4 * * * cd /path/to/project && claude --print -p "Check health of dc-01, web-lb-01, dns-primary and tag the results (1h window)" --allowedTools "mcp__extrahop__*"
```

## Claude Desktop — Routines

For recurring checks on a workstation.

1. Routines sidebar → New routine → Local
2. Name: `extrahop-health-check`
3. Instructions: `Run a full environment network health check and tag the results`
4. Schedule: e.g. daily at 8:00 AM
5. Working folder: project directory with `.claude/` config and ExtraHop MCP
6. Run once manually to approve permission prompts

Enable "Keep computer awake" for reliability. Missed runs get a single catch-up on wake.

## Claude.ai — Cloud Routines

For 24/7 monitoring without a workstation. Requires Pro, Max, Team, or Enterprise.

**Prerequisite:** ExtraHop MCP must be reachable from Anthropic's cloud — either a remote MCP server (HTTPS) or a connector bridging to your on-prem appliance. Local stdio MCP binaries won't work.

```
/schedule daily at 8am Run a full environment network health check and tag the results
/schedule every 4 hours Check health of dc-01, web-lb-01, dns-primary and tag the results
```

## GitHub Copilot Workspace / Copilot Chat

No first-class scheduling primitive for chat-based agents. Use:

- **CI cron** (GitHub Actions `schedule:`) calling a script that drives Copilot CLI with the health-check prompt
- **External scheduler** (Windows Task Scheduler, launchd, cron) invoking Copilot CLI
- **Manual on-demand** for ad-hoc investigations

MCP server must be configured where Copilot CLI runs.

## Gemini CLI / Gemini Code Assist

- **`gemini` CLI with cron** — same pattern as Claude Code; invoke `gemini -p "<prompt>"` with ExtraHop MCP in `~/.gemini/settings.json`
- **Workspace-side scheduling** — not currently available; use OS-level scheduling

## Generic / Custom Integrations

Any agent platform supporting MCP and accepting a text prompt can run scheduled checks via an external scheduler (cron, systemd timers, Kubernetes CronJobs, cloud schedulers). The prompt and skill logic are identical; only the invocation wrapper changes.

For containerized scheduling, the container must:

1. Have network reachability to the ExtraHop appliance(s)
2. Have the ExtraHop MCP server installed and configured
3. Have credentials mounted (don't bake API keys into images)
4. Log output to a durable location for audit

## Best Practices

- **Match window to interval.** Hourly runs → 1h window; daily → 24h. Mismatches cause double-counting or gaps.
- **Always tag.** Without tagging, scheduled runs produce reports nobody reads. With tagging, unhealthy devices surface in the ExtraHop UI between runs.
- **Stagger fleet protocol checks.** Don't run environment + protocol DNS + protocol HTTP all at top of the hour — they hit the same sensors.
- **Watch baseline boundary effects.** Daily Monday 8am compares to Sunday 8am — rarely fair. Use same-day-last-week for ≥24h windows.
- **Set failure alerting on the scheduler.** If the scheduled job stops running, you want to know.
