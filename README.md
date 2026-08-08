# trebon-sites

Monorepo for three related Třeboň wellness/wellness websites: masáže, thajské masáže, and ubytování. All share a unified tech stack (static HTML + JS, nginx via Docker, Caddy TLS on VPS) and a common reservation system.

## Sites

| Site | Domain | Status |
|------|--------|--------|
| **Masáže Jana Tondlová** | www.masaze-trebon.cz | Design spec complete |
| **Thajské masáže Třeboň** | www.thajskemasaze-trebon.cz | Design spec complete |
| **U Třeboňské madony** | www.utrebonskemadony.cz | Design spec complete |

## Tech Stack

- **Frontend:** Static HTML + inline CSS + vanilla JS (zero build step, zero framework)
- **Server:** nginx:alpine in Docker
- **TLS:** Caddy on VPS host, reverse-proxying to Docker containers
- **Booking:** Previo REST API (via nginx reverse proxy)
- **Languages:** CZ / EN / DE per site
- **SEO:** Schema.org JSON-LD, hreflang tags, structured data

## Architecture

```
trebon-sites/
├── sites/                         # Per-site source code
│   ├── masaze-trebon/             #   HTML, CSS, JS, Dockerfile, nginx.conf
│   ├── thajskemasaze-trebon/
│   └── utrebonskemadony/
├── shared/                        # Shared infrastructure
│   ├── docker/                    #   docker-compose.yml, Dockerfile.template
│   └── nginx/                     #   Shared nginx.conf template
├── handovers/                     # Relay payloads and completion reports
│   ├── _relay_template.json       #   Current best template (evolved via learnings)
│   ├── done/
│   └── archive/
├── learnings/                     # Per-step subagent observations
├── AGENTS.md                      # Tiered Relay Architecture v4 protocol
├── .internal_master_plan.md       # Architect-only plan (gitignored)
└── devlog.md                      # Subagent activity log (gitignored)
```

## Development Flow

This project uses the **Tiered Relay Architecture v4** — a plan → delegate → verify loop where the Master Architect (Hermes) plans and verifies, and subagents execute code changes.

1. **Plan** — update `.internal_master_plan.md` with step breakdown
2. **Delegate** — write JSON relay payload, dispatch to subagent via `delegate_task`
3. **Verify** — re-execute tests independently, audit handover, gate decision
4. **Learn** — record observations in `learnings/`, evolve `_relay_template.json`

Full protocol: [`AGENTS.md`](AGENTS.md)

## Infrastructure

### VPS

- Host: srv1773137.hstgr.cloud
- Tailscale IP: 100.120.152.61
- Docker network: `hermes_caddy-net`
- Caddy handles TLS termination

### Local Dev

```bash
# Start all three sites
docker compose -f shared/docker/docker-compose.yml up -d

# Single site
cd sites/masaze-trebon && docker build -t masaze-trebon . && docker run -p 8080:80 masaze-trebon
```
