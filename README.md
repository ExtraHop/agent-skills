# ExtraHop Agent Skills

A growing collection of Agent Skills that unlock your ExtraHop network telemetry and context for agentic AI workflows.

Each skill is purpose-built to work with the [ExtraHop MCP Server](https://github.com/ExtraHop/agent-mcp) and knows how to drive RevealX tools the right way, so you get accurate, context-aware answers instead of generic AI guesswork. The MCP Server is the recommended path, but the skills aren't tied to it: they can just as well drive the [ExtraHop CLI](https://github.com/ExtraHop/agent-cli) or call the RevealX REST API directly, so they fit whatever setup you already have. Install them into Claude Desktop, Claude Code, Gemini Antigravity, or any MCP-compatible AI client.

## Getting Started

### Install (Claude Desktop)

Each skill is packaged as a `.zip` file. Download a skill's `.zip` from the project's Releases page, or build one from a clone with `zip -r extrahop-triage.zip extrahop-triage` (zips are release artifacts, not tracked in the repo). Then, in Claude Desktop:

1. Go to **Customize → Skills → Add skill → Create skill → Upload a skill**
2. Drag in the skill's `.zip`

No server setup is required beyond having the ExtraHop MCP Server already connected.

### Install (Claude Code)

Install from a local clone. Each skill is its own directory at the repository root:

```bash
git clone https://github.com/ExtraHop/agent-skills.git
cd agent-skills

# Copy the skills you want into your Claude Code skills directory
mkdir -p ~/.claude/skills
cp -R extrahop-app-discovery extrahop-health-check extrahop-rest-api \
      extrahop-triage extrahop-pqc-tls-readiness ~/.claude/skills/
```

Changes take effect on the next session.

### Install (Gemini Antigravity)

Antigravity discovers skills in `~/.gemini/config/skills/` (macOS) or `%USERPROFILE%\.gemini\config\skills\` (Windows). Copy each skill directory from your clone into it:

**macOS**

```bash
git clone https://github.com/ExtraHop/agent-skills.git
cd agent-skills

mkdir -p ~/.gemini/config/skills
cp -R extrahop-app-discovery extrahop-health-check extrahop-rest-api \
      extrahop-triage extrahop-pqc-tls-readiness ~/.gemini/config/skills/
```

**Windows** (from the cloned `agent-skills` directory)

```cmd
mkdir "%USERPROFILE%\.gemini\config\skills"

xcopy /E /I extrahop-app-discovery     "%USERPROFILE%\.gemini\config\skills\extrahop-app-discovery"
xcopy /E /I extrahop-health-check      "%USERPROFILE%\.gemini\config\skills\extrahop-health-check"
xcopy /E /I extrahop-rest-api          "%USERPROFILE%\.gemini\config\skills\extrahop-rest-api"
xcopy /E /I extrahop-triage            "%USERPROFILE%\.gemini\config\skills\extrahop-triage"
xcopy /E /I extrahop-pqc-tls-readiness "%USERPROFILE%\.gemini\config\skills\extrahop-pqc-tls-readiness"
```

Each skill folder must contain a `SKILL.md` at its root. Verify with `find ~/.gemini/config/skills -name "SKILL.md"` (macOS) or `dir /s /b "%USERPROFILE%\.gemini\config\skills\SKILL.md"` (Windows). Restart Antigravity to load the skills; it invokes the right one automatically based on your prompt.

### Other Clients

These skills are plain markdown. Any MCP-compatible AI client that can load Agent Skills can use them: point your tool at the skill directories in your clone (each is a top-level folder containing a `SKILL.md`).

## Skills

This collection grows over time; the table below is a sample of what's available, not the full list. Browse the repository's top-level skill directories for everything currently published, and check each skill's `SKILL.md` for its complete description and example prompts.

| Skill | Purpose |
|-------|---------|
| `extrahop-triage` | Triage and investigate security detections: separate false positives from true positives, reconstruct attack chains, close noisy detections, and create RevealX investigation cases |
| `extrahop-health-check` | Run role-aware network and service health checks: root-cause slow apps, auth failures, DNS/HTTP/Kerberos/LDAP/SMB/database issues, and overall infrastructure health |
| `extrahop-app-discovery` | Discover and map enterprise applications from network traffic: trace app tiers, backend pools behind a VIP, and shadow IT, with device-group and tagging recommendations |
| `extrahop-rest-api` | Generate Python (`requests`) code for RevealX 360 REST API endpoints not covered by the MCP Server: alerts, triggers, dashboards, watchlists, custom devices, and more |
| `extrahop-pqc-tls-readiness` | Inventory internal TLS servers (and optionally clients) and assess Post-Quantum Cryptography (PQC) key exchange readiness: which servers and clients were observed using PQC, unique PQC vs. non-PQC client counts, and which named groups (ML-KEM vs. Kyber) were used, as CSV or a self-contained HTML report |

> **Note:** `extrahop-rest-api` and `extrahop-pqc-tls-readiness` have RevealX 26.3 dependencies and release July 2026.

Many of these skills complement each other: **App Discovery** hands off to **Health Check** for performance questions and to **Triage** for security concerns, while **REST API** fills in anything the MCP tools don't cover. Install just the ones you need, or all of them.

## Usage

A few skills are highlighted below to show the range of what's possible; this isn't the complete set. Each skill activates automatically when your prompt matches what it does, so you rarely need to name it explicitly.

### Detection Triage (`extrahop-triage`)

Triage and investigate security detections in ExtraHop RevealX. Separates false positives from malicious and benign true positives, reconstructs attack chains, closes noisy detections, and creates RevealX investigation cases. Use for NDR detections, SOC detection triage, alert noise reduction, or incident investigation.

Try it with:

```
Show me today's detections
Find false positives I can close
Find the ones worth digging into and investigate anything that looks serious
Investigate this detection
```

### Health Check (`extrahop-health-check`)

Run accurate, role-aware network and service health checks against a RevealX environment. Activates on questions about the state of your network, application performance, or infrastructure health, including symptom descriptions like slow sites, login issues, timeouts, file-share problems, TCP retransmissions, packet loss, authentication failures, or account lockouts.

Try it with:

```
Run a health check on vip-bk-05
Assess overall network infrastructure health trends
Health check app-x-group last 7d
Are DNS services degraded?
```

### App Discovery (`extrahop-app-discovery`)

Discover and map enterprise applications based on network traffic analyzed by RevealX. Maps application tiers (web/app/database), traces the backend server pool behind a load balancer or VIP, identifies services by HTTP host/URI or TLS SNI, and surfaces undocumented dependencies and shadow IT. Discovery is read-only and advisory: it observes traffic and recommends a model with device tags and device groups; it does not create groups.

Try it with:

```
What applications pass through this VIP?
What apps are running in 10.20.0.0/16?
Map the checkout service
How should I group these servers?
```

### REST API (`extrahop-rest-api`)

Generate Python code (using `requests`) to call the RevealX 360 REST API for endpoints the MCP Server doesn't expose: alerts, triggers, dashboards, reports, activity maps, exclusion intervals, watchlists, custom devices, network localities, bundles, threat collections, ODS targets, users, API keys, audit logs, and any `/api/v1` endpoint. Use when you want a script you can save and rerun, or when the answer isn't obviously an MCP tool.

Try it with:

```
How do I create an exclusion interval in ExtraHop?
Write a script to export all alerts to CSV
Add these IPs to a watchlist
```

### PQC TLS Readiness (`extrahop-pqc-tls-readiness`)

Inventory internal TLS servers and assess Post-Quantum Cryptography (PQC) key exchange readiness from RevealX metrics. Reports whether a PQC key exchange was *observed* on each server in the window (observation, not a capability claim: no PQC seen doesn't prove a server can't do it), counts unique clients that used PQC vs. non-PQC key exchanges, and can optionally break down *which* named groups were used (standardized ML-KEM vs. pre-standard Kyber) and assess the client side, which of your own endpoints were observed initiating PQC. Output is a per-device CSV or a self-contained, print-ready HTML report built from a bundled brandable template; official ExtraHop branding is an optional add-on (`extrahop-artifacts`), available on request but not required. Read-only and metrics-first: it filters out external devices and aggregates each device's per-sensor copies by `extrahop_id` so counts reflect real internal hosts. Requires RevealX 26.3, where the `post_quantum_kex` metric is available.

Try it with:

```
Assess our post-quantum TLS readiness
Which servers haven't negotiated PQC yet?
Which of my clients were observed initiating PQC key exchange?
Generate a PQC readiness report as HTML
```

## License

Each skill is MIT-licensed; see the `LICENSE` file inside each skill directory (e.g. [`extrahop-triage/LICENSE`](extrahop-triage/LICENSE)) for details.

## Related Repositories

- ExtraHop/agent-skills (this repository)
- [ExtraHop/agent-mcp](https://github.com/ExtraHop/agent-mcp)
- [ExtraHop/agent-cli](https://github.com/ExtraHop/agent-cli)
