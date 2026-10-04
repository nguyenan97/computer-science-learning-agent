#!/usr/bin/env python3
"""Validate bilingual Docsify navigation and route/file consistency."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAV_FILES = [
    ROOT / "_sidebar.md",
    ROOT / "_navbar.md",
    ROOT / "vi/_sidebar.md",
    ROOT / "vi/_navbar.md",
]
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)\s]+)(?:\s+[^)]*)?\)")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "tel:")


def internal_routes(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [target for target in LINK_RE.findall(text) if not target.startswith(EXTERNAL_PREFIXES)]


def route_candidates(route: str) -> list[Path]:
    clean = route.split("?", 1)[0].split("#", 1)[0]
    if not clean.startswith("/"):
        return []

    relative = clean.lstrip("/")
    if not relative:
        return [ROOT / "README.md"]
    if clean.endswith("/"):
        return [ROOT / relative / "README.md"]
    if relative.endswith(".md"):
        return [ROOT / relative]
    return [ROOT / f"{relative}.md", ROOT / relative / "README.md"]


def validate_navigation_file(path: Path, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"missing navigation file: {path.relative_to(ROOT)}")
        return

    for target in internal_routes(path):
        if target.startswith("#/") or target.startswith("#"):
            errors.append(
                f"{path.relative_to(ROOT)}: use Docsify route links such as '/vi/' or '/references/page', not '{target}'"
            )
            continue
        if not target.startswith("/"):
            errors.append(
                f"{path.relative_to(ROOT)}: internal navigation link must be root-relative: '{target}'"
            )
            continue

        candidates = route_candidates(target)
        if not candidates or not any(candidate.exists() for candidate in candidates):
            rendered = ", ".join(str(candidate.relative_to(ROOT)) for candidate in candidates)
            errors.append(
                f"{path.relative_to(ROOT)}: route '{target}' has no Markdown target (checked: {rendered})"
            )


def validate_sidebar_roles(errors: list[str]) -> None:
    en = (ROOT / "_sidebar.md").read_text(encoding="utf-8")
    vi = (ROOT / "vi/_sidebar.md").read_text(encoding="utf-8")
    if "**Language**" in en or "**Ngôn ngữ**" in en:
        errors.append("_sidebar.md must not contain the language switcher; use _navbar.md")
    if "**Language**" in vi or "**Ngôn ngữ**" in vi:
        errors.append("vi/_sidebar.md must not contain the language switcher; use vi/_navbar.md")


def normalized_sidebar_routes(path: Path, locale_prefix: str = "") -> list[str]:
    routes = []
    for target in internal_routes(path):
        if target in ("/", "/vi/"):
            continue
        clean = target.rstrip("/")
        if locale_prefix and clean.startswith(locale_prefix):
            clean = clean[len(locale_prefix):] or "/"
        routes.append(clean)
    return routes


def validate_language_mirror(errors: list[str]) -> None:
    en_routes = normalized_sidebar_routes(ROOT / "_sidebar.md")
    vi_routes = normalized_sidebar_routes(ROOT / "vi/_sidebar.md", "/vi")
    if en_routes != vi_routes:
        errors.append(
            "English and Vietnamese sidebars are not route mirrors:\n"
            f"  EN: {en_routes}\n"
            f"  VI: {vi_routes}"
        )

    en_nav = internal_routes(ROOT / "_navbar.md")
    vi_nav = internal_routes(ROOT / "vi/_navbar.md")
    if "/vi/" not in en_nav:
        errors.append("_navbar.md must link to the Vietnamese language root '/vi/'")
    if "/" not in vi_nav:
        errors.append("vi/_navbar.md must link to the English language root '/'")


def validate_docsify_config(errors: list[str]) -> None:
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    required = {
        "routerMode: 'hash'": "Docsify must use hash routing on GitHub Project Pages",
        "loadSidebar: true": "Docsify sidebar must be enabled",
        "loadNavbar: true": "Docsify navbar must be enabled",
        "navbarPreservePath: true": "language switching should preserve the current document path",
    }
    for snippet, message in required.items():
        if snippet not in index:
            errors.append(f"index.html: {message} (missing `{snippet}`)")

    if "language-switcher" in index:
        errors.append("index.html: custom language-switcher must not be used; language navigation belongs in _navbar.md")


def main() -> int:
    errors: list[str] = []

    for path in NAV_FILES:
        validate_navigation_file(path, errors)

    validate_sidebar_roles(errors)
    validate_language_mirror(errors)
    validate_docsify_config(errors)

    if errors:
        print("Documentation navigation validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Docsify navigation is valid: EN/VI routes resolve and language switching is navbar-based.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
