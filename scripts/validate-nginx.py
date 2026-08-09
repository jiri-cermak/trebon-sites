#!/usr/bin/env python3
"""
nginx config structural validator for trebon-sites.
Replaces the need for `nginx -t` in the development container (no nginx installed).
Catches: unbalanced braces, missing semicolons, wrong domain→dir mapping,
         missing required directives, COPY directive coverage in Dockerfile.

Usage:
    python3 scripts/validate-nginx.py              # validate everything
    python3 scripts/validate-nginx.py --nginx-only  # nginx configs only
    python3 scripts/validate-nginx.py --quiet       # exit code only, no output

Exit 0 = valid. Exit 1 = errors found.

Called from relay testing methodology:
    cd /opt/data/projects/trebon-sites && python3 scripts/validate-nginx.py
"""

import os, re, sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent


# ── helpers ─────────────────────────────────────────────────────────────

def _lines(text: str) -> list[str]:
    return [l.strip() for l in text.splitlines()]

def _strip_comments(line: str) -> str:
    """Remove inline comments but preserve quoted '#'."""
    in_quote = False
    result = []
    for ch in line:
        if ch in ('"', "'"):
            in_quote = not in_quote
            result.append(ch)
        elif ch == '#' and not in_quote:
            break
        else:
            result.append(ch)
    return ''.join(result).rstrip()

def _braces_balanced(text: str, label: str) -> list[str]:
    """Return list of error messages or empty list."""
    errs = []
    depth = 0
    for i, ch in enumerate(text):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
        if depth < 0:
            lineno = text[:i].count('\n') + 1
            errs.append(f"{label}: unbalanced '}}' at line {lineno}")
            depth = 0  # reset so we keep checking
    if depth > 0:
        errs.append(f"{label}: {depth} unclosed '{{' brace(s)")
    return errs

def _directive_semicolons(text: str, label: str) -> list[str]:
    """Check that non-block directives end with ';'."""
    errs = []
    for i, raw in enumerate(text.splitlines(), 1):
        line = _strip_comments(raw)
        stripped = line.strip()
        if not stripped:
            continue
        # Skip block openers/closers and lines ending with { or }
        if stripped.endswith('{') or stripped.endswith('}'):
            continue
        # Skip lines that are just comments now
        if stripped.startswith('#'):
            continue
        # Skip 'include' lines (they end with the included file path + ';')
        if stripped.startswith('include '):
            if not stripped.endswith(';'):
                errs.append(f"{label}:{i}: 'include' directive missing ';'")
            continue
        # All other directives must end with ;
        if not stripped.endswith(';'):
            errs.append(f"{label}:{i}: directive missing ';': {stripped[:60]}")
    return errs

def _has_directive(text: str, directive: str) -> bool:
    """Check directive exists (word boundary aware)."""
    pattern = rf'(?:^|\s){re.escape(directive)}(?:\s|;)'
    return bool(re.search(pattern, text, re.MULTILINE))

def _count_directive(text: str, directive: str) -> int:
    pattern = rf'(?:^|\s){re.escape(directive)}(?:\s|;)'
    return len(re.findall(pattern, text, re.MULTILINE))


# ── nginx.conf checks ──────────────────────────────────────────────────

def validate_nginx_conf() -> list[str]:
    path = PROJECT / "nginx.conf"
    if not path.exists():
        return [f"MISSING: {path}"]
    text = path.read_text()
    errs = []

    # Structural
    errs += _braces_balanced(text, "nginx.conf")
    errs += _directive_semicolons(text, "nginx.conf")

    # Must have exactly 3 server blocks
    server_count = _count_directive(text, "server")
    if server_count != 3:
        errs.append(f"nginx.conf: expected 3 server blocks, found {server_count}")

    # Each server block must include shared.conf
    include_count = text.count("include /etc/nginx/conf.d/shared.conf")
    if include_count != 3:
        errs.append(f"nginx.conf: expected 3 'include' of shared.conf, found {include_count}")

    # Domain → root mapping (V5 Section 0.4)
    expected = [
        ("utrebonskemadony.cz", "penzion"),
        ("thajskemasaze-trebon.cz", "thai"),
        ("masaze-trebon.cz", "masaze"),
    ]
    for domain, subdir in expected:
        if domain not in text:
            errs.append(f"nginx.conf: missing server_name '{domain}'")
        expected_root = f"root /usr/share/nginx/html/{subdir}"
        if expected_root not in text:
            errs.append(f"nginx.conf: missing '{expected_root}' for {domain}")

    # Each server block must have index
    if _count_directive(text, "index") < 3:
        errs.append("nginx.conf: not all server blocks have 'index index.html'")

    # listen must be 80
    if _count_directive(text, "listen 80") < 3:
        errs.append("nginx.conf: not all server blocks 'listen 80'")

    return errs


# ── shared.conf checks ─────────────────────────────────────────────────

def validate_shared_conf() -> list[str]:
    path = PROJECT / "shared.conf"
    if not path.exists():
        return [f"MISSING: {path}"]
    text = path.read_text()
    errs = []

    errs += _braces_balanced(text, "shared.conf")
    errs += _directive_semicolons(text, "shared.conf")

    # Security headers (V5 Section 0.4)
    for header in ["X-Frame-Options", "X-Content-Type-Options", "Referrer-Policy"]:
        if header not in text:
            errs.append(f"shared.conf: missing security header '{header}'")

    # Cache directives for all 4 static asset dirs
    for d in ["css", "js", "img", "fonts"]:
        if f"location /{d}/" not in text:
            errs.append(f"shared.conf: missing cache location for /{d}/")
    if "expires 1y" not in text:
        errs.append("shared.conf: missing 'expires 1y' cache directive")
    if "Cache-Control" not in text:
        errs.append("shared.conf: missing 'Cache-Control' header")

    # API proxy stubs (Phase 2, but locations should exist now)
    for proxy in ["/api/previo/", "/api/booking/", "/api/shop/"]:
        if proxy not in text:
            errs.append(f"shared.conf: missing API proxy location '{proxy}'")

    # Static files
    for f in ["robots.txt", "sitemap.xml", "llms.txt"]:
        if f not in text:
            errs.append(f"shared.conf: missing location for '{f}'")

    # 404
    if "error_page 404" not in text:
        errs.append("shared.conf: missing 'error_page 404' directive")

    return errs


# ── Dockerfile checks ───────────────────────────────────────────────────

def validate_dockerfile() -> list[str]:
    path = PROJECT / "Dockerfile"
    if not path.exists():
        return [f"MISSING: {path}"]
    text = path.read_text()
    errs = []

    if "FROM nginx:alpine" not in text:
        errs.append("Dockerfile: missing or wrong base image (expected nginx:alpine)")

    # All directories from V5 Section 0.2 must be COPY'd
    required_copies = [
        "COPY penzion/ thai/ masaze/ /usr/share/nginx/html/",
        "COPY css/",
        "COPY js/",
        "COPY img/",
        "COPY fonts/",
        "COPY nginx.conf /etc/nginx/conf.d/default.conf",
        "COPY shared.conf /etc/nginx/conf.d/shared.conf",
    ]
    for cp in required_copies:
        if cp not in text:
            errs.append(f"Dockerfile: missing '{cp.split('/')[0]}' ...")

    return errs


# ── main ────────────────────────────────────────────────────────────────

def main() -> int:
    quiet = "--quiet" in sys.argv
    nginx_only = "--nginx-only" in sys.argv

    all_errs = []
    all_errs += validate_nginx_conf()
    all_errs += validate_shared_conf()

    if not nginx_only:
        all_errs += validate_dockerfile()

    if all_errs:
        if not quiet:
            print(f"VALIDATION FAILED — {len(all_errs)} error(s):\n")
            for e in all_errs:
                print(f"  ✗ {e}")
            print(f"\nFix {len(all_errs)} error(s) and re-run.")
        return 1
    else:
        if not quiet:
            checked = "nginx.conf + shared.conf" if nginx_only else "nginx.conf + shared.conf + Dockerfile"
            print(f"✓ {checked} — all checks passed")
        return 0


if __name__ == "__main__":
    sys.exit(main())
