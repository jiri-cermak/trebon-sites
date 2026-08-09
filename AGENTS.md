# Tiered Relay Architecture v6 — trebon-sites Adapter

Read `CORE_PROTOCOL.md` first. This file contains only project-specific adapter rules for `/opt/data/projects/trebon-sites`; it is not the reusable orchestration core.

## Adapter identity

- **Project:** trebon-sites
- **Root:** `/opt/data/projects/trebon-sites`
- **Stack:** static HTML/CSS/vanilla JavaScript, one nginx container, shared CSS/JS/fonts/images
- **Primary execution profile:** Architect delegates web implementation to `deepseek-v4-flash` where configured; record the actual model/provider in telemetry and do not treat this preference as a core rule.
- **Reference specification:** `/opt/data/projects/redesign/NEW_V5_design_specification.md`
- **Domains:** `www.masaze-trebon.cz`, `www.thajskemasaze-trebon.cz`, `www.utrebonskemadony.cz`

## Project structure

- `thai/` — Thai massage site
- `penzion/` — accommodation site
- `masaze/` — classic massage/wellness site
- `css/design-system.css` — shared design system
- `js/main.js` — shared vanilla JavaScript
- `fonts/` — self-hosted WOFF2 fonts
- `img/` — photos and shared image assets
- `nginx.conf`, `shared.conf`, `Dockerfile` — infrastructure
- `handovers/`, `learnings/` — Architect-side state

## Local bootstrap guard

Before delegating:

```bash
cd /opt/data/projects/trebon-sites
pwd
git rev-parse --show-toplevel
git status --short
```

The repository must exist and the working tree must be understood before a relay starts. Internal state must be excluded. The `img/` directory is intentionally currently untracked; do not stage it unless a relay explicitly names the required asset files.

## Protected files

Do not modify unless the relay explicitly names them:

- `AGENTS.md`
- `CORE_PROTOCOL.md`
- `.internal_master_plan.md`
- `devlog.md`
- `handovers/`
- `learnings/`
- `.git/`
- `css/design-system.css`
- `nginx.conf`
- `shared.conf`
- `Dockerfile`
- `scripts/`
- `fonts/`
- `img/` as a directory; individual asset files require explicit target paths

## Local boundaries

- **Allowed tools:** Python 3 stdlib, `git`, `curl`, `grep`, Hermes browser/console tools when available, and project-approved shell/process commands.
- **Unavailable or forbidden in subagent tests:** npm packages, build frameworks, pip installation, apt installation, Fontsource CDN, and Docker recovery/install attempts.
- **Tool replacements:** use Python stdlib for archive, byte, metadata, parsing, comparison, and file operations where the container lacks `xxd`, `od`, `unzip`, `file`, `jq`, `sed`, `awk`, `stat`, `diff`, `find`, `sort`, `head`, `tail`, `cut`, `tar`, or checksum tools. `od` is explicitly forbidden after the STEP-06 observation.
- **Dependencies:** no npm, no pip, no apt, no React/Vue/Svelte, no CSS framework, no build step. Self-host WOFF2 fonts. Google WebFonts Helper API may be used only for an explicitly scoped font-download relay.
- **Server policy:** Docker is unavailable in the subagent environment. Use `python3 -m http.server` for local runtime tests. Docker/VPS verification is Architect-side only when explicitly required.
- **External resources:** pages should remain static and avoid undeclared external embeds/dependencies. Project-specific SEO and domain rules come from the referenced specification and the relay.

## Local testing adapter

Every relay must include exact commands satisfying the core verification levels:

1. **Structural:** Python/HTMLParser/regex or another runtime assertion over the output shape.
2. **Negative:** explicitly test forbidden dependency, forbidden element, unlisted file mutation, or invalid state.
3. **Runtime:** start `python3 -m http.server PORT --bind 127.0.0.1` via the terminal background process tool and check HTTP responses with `curl`.
4. **Browser/DOM:** required for HTML/CSS/JS changes. Use `browser_navigate`, `browser_console`, JS error inspection, computed styles, DOM shape, image `naturalWidth`, and timing/state checks such as carousel rotation.
5. **Visual screenshot:** optional. If `browser_vision` fails, do not retry the provider; fall back to browser console and DOM/property checks.

Additional local conventions:

- CSS assertions must tolerate valid whitespace (`property.*value`, not only `property:value`).
- Verification scripts belong under `/opt/data/`, not `/tmp/`.
- Preserve complete raw test output in the handover.
- For terminal-masked phone digits, verify the file bytes/content with Python rather than modifying correct digits.
- Negative scans must include comments and markup when a banned string is forbidden; do not hide banned strings in comments.
- FAQ or other verbatim copy contracts require exact string assertions, including `&nbsp;` and en dashes.

## Local handover additions

Use the core's exact five headings. In addition, report:

- browser/DOM checks for all UI or JS changes;
- any intentionally untracked asset dependencies;
- explicit staged file list before commit;
- model/provider and thinking mode;
- parallel delegation when used and its dependency rationale.

## Local learning register

Store observations in `learnings/`. Classify every observation as `core`, `adapter`, `project-specific`, or `historical`.

Current adapter learnings from Plausit and trebon-sites:

- direct context is the active delegation mechanism;
- absolute paths and first-command `pwd`/repository-root verification are mandatory;
- browser/DOM checks materially improve HTML/CSS/JS verification;
- `browser_vision` is optional because the current provider may fail;
- `img/` remains untracked until an explicit asset commit;
- use explicit `git add` target paths only;
- batch only independent steps with no shared target files;
- `deepseek-v4-flash` was stronger than PRO in the measured visual Phase B run, but this remains telemetry/adapter evidence, not a universal core rule.

Only genuinely project-agnostic observations may be proposed for propagation into `CORE_PROTOCOL.md`.

## Operating rule

`CORE_PROTOCOL.md` defines the orchestration lifecycle, evidence gates, retry behavior, git safety, and learning lifecycle. This adapter defines trebon-sites. If they conflict, stop and resolve the ambiguity before delegation.

See also: `handovers/_relay_context_template.md`, `.internal_master_plan.md`, `devlog.md`, and the referenced design specification.
ಮು

## Migration note

This project was migrated from the v5 trebon-sites protocol to v6. Historical handovers and learnings retain their original protocol labels; they are evidence, not rewritten history.

## Adapter review status

- Migration source: GitHub template `jiri-cermak/agentic_dev_template`, v6 commit `380eae4`.
- Migration scope: core separation, explicit local adapter, verification taxonomy, learning classification, CWD protection, and staging safety.
- No feature files or completed historical handovers were changed by this migration.
