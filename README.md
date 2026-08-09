# trebon-sites

Monorepo for three Třeboň wellness/wellness websites: masáže, thajské masáže, ubytování. Single nginx container serves all three domains via `server_name` routing. Shared CSS, JS, fonts, and images across the ecosystem.

## Sites

| Site | Directory | Domain | `data-site` |
|------|-----------|--------|-------------|
| **Masáže Jana Tondlová** | `masaze/` | www.masaze-trebon.cz | `masaze` |
| **Thajské masáže Třeboň** | `thai/` | www.thajskemasaze-trebon.cz | `thai` |
| **U Třeboňské madony** | `penzion/` | www.utrebonskemadony.cz | `penzion` |

## Tech Stack

- **Frontend:** Static HTML + single shared `css/design-system.css` + vanilla JS (zero build step, zero framework)
- **Server:** Single `nginx:alpine` container, `server_name` routing to subdirectories
- **TLS:** Caddy on VPS host, reverse-proxying all three domains to `trebon-sites:80`
- **Booking:** Previo REST API via nginx reverse proxy (Phase 2), Previó iframe embed (Phase 1)
- **Languages:** CZ / EN / DE per site
- **SEO:** Schema.org JSON-LD, hreflang tags, llms.txt
- **Design:** `data-site` attribute drives per-domain color theming (Section 2.3 of V5 spec)

## Architecture

```
trebon-sites/
├── masaze/                    # masaze-trebon.cz — Classic Wellness JT
│   ├── index.html
│   ├── masaze/                # procedure listing
│   ├── koupele/               # baths
│   ├── rezervace/
│   ├── faq/
│   ├── kontakt/
│   ├── en/                    # EN mirror
│   ├── de/                    # DE mirror
│   ├── robots.txt
│   ├── sitemap.xml
│   └── llms.txt
├── thai/                      # thajskemasaze-trebon.cz — Authentic Thai
│   └── ...                    # same structure as masaze
├── penzion/                   # utrebonskemadony.cz — Boutique Hotel
│   └── ...                    # same structure as masaze + pokoje/ + season matrix
├── css/
│   └── design-system.css      # single source of truth (Sections 2–8 of V5 spec)
├── js/
│   ├── i18n.js                # translation dictionary
│   ├── availability.js        # Previo API client (penzion)
│   ├── booking.js             # jong API client (thai + masaze, Phase 2)
│   └── main.js                # navigation, language switcher, sheet drawer
├── img/
│   ├── logo-penzion.svg       # external SVG, browser-cacheable
│   ├── logo-thai.svg
│   ├── logo-masaze.svg
│   ├── icons/                 # SVG icon library (24×24, currentColor)
│   └── photos/                # WebP + JPEG fallback
├── fonts/                     # self-hosted WOFF2, subset Latin+Czech
├── nginx.conf                 # 3 server blocks, server_name routing
├── shared.conf                # security headers, cache, API proxies
├── Dockerfile                 # nginx:alpine, single container
├── handovers/                 # Relay payloads and completion reports
│   ├── _relay_template.json
│   ├── done/
│   └── archive/
├── learnings/                 # Per-step subagent observations
├── AGENTS.md                  # Tiered Relay Architecture v4 protocol
├── .internal_master_plan.md   # Architect-only plan (gitignored)
└── devlog.md                  # Subagent activity log (gitignored)
```

## Development Flow

This project uses the **Tiered Relay Architecture v4** — a plan → delegate → verify loop where the Master Architect (Hermes) plans and verifies, and subagents execute code changes.

1. **Plan** — update `.internal_master_plan.md` with step breakdown
2. **Delegate** — write JSON relay payload, dispatch to subagent via `delegate_task`
3. **Verify** — re-execute tests independently, audit handover, gate decision
4. **Learn** — record observations in `learnings/`, evolve `_relay_template.json`

Full protocol: [`AGENTS.md`](AGENTS.md)

## Design System

See `/opt/data/projects/redesign/NEW_V5_design_specification.md` for the full 1809-line spec covering:
- Design tokens & CSS custom properties with `data-site` per-domain theming
- UI component library (cards, price tables, accordion, forms, testimonials)
- Responsive layout (desktop sidebar → tablet card → mobile slide-up sheet)
- GEO/AI agent optimization (JSON-LD, llms.txt, E-E-A-T blocks)
- 6-phase implementation roadmap

## Infrastructure

### VPS

- Host: srv1773137.hstgr.cloud
- Tailscale IP: 100.120.152.61
- Docker network: `hermes_caddy-net`
- Caddy handles TLS termination, reverse-proxies to `trebon-sites:80`

### Local Dev

```bash
# Volume-mount for rapid iteration (no rebuild)
docker run -d \
  --name trebon-sites \
  --restart unless-stopped \
  --network hermes_caddy-net \
  -v /opt/data/projects/trebon-sites/nginx.conf:/etc/nginx/conf.d/default.conf:ro \
  -v /opt/data/projects/trebon-sites/shared.conf:/etc/nginx/conf.d/shared.conf:ro \
  -v /opt/data/projects/trebon-sites/:/usr/share/nginx/html:ro \
  nginx:alpine

# Or build and run
docker build -t trebon-sites . && docker run -p 8080:80 trebon-sites
```
