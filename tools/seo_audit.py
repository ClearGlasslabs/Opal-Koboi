#!/usr/bin/env python3
"""Deterministic SEO QA for the ClearGlass static production surface.

The default mode reports both errors and warnings and exits non-zero only for
errors. Use --strict to promote warnings to a non-zero exit for dedicated SEO
hardening work.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

PRODUCTION_ORIGIN = "https://www.clearglassinc.com"
DEFAULT_INDEXABLE_PAGES = ("index.html", "CG-os.html")
DESCRIPTION_MIN = 70
DESCRIPTION_MAX = 180
TITLE_MIN = 20
TITLE_MAX = 70


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    message: str


class SEOParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.in_title = False
        self.h1_count = 0
        self.meta: dict[str, str] = {}
        self.properties: dict[str, str] = {}
        self.canonicals: list[str] = []
        self.json_ld_blocks: list[str] = []
        self._json_ld = False
        self._json_ld_parts: list[str] = []
        self.images: list[dict[str, str]] = []

    @property
    def title(self) -> str:
        return " ".join(part.strip() for part in self.title_parts if part.strip()).strip()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): (value or "") for key, value in attrs}
        tag = tag.lower()
        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "meta":
            name = values.get("name", "").lower()
            prop = values.get("property", "").lower()
            content = values.get("content", "").strip()
            if name:
                self.meta[name] = content
            if prop:
                self.properties[prop] = content
        elif tag == "link":
            rel_tokens = {token.lower() for token in values.get("rel", "").split()}
            if "canonical" in rel_tokens and values.get("href"):
                self.canonicals.append(values["href"].strip())
        elif tag == "script" and values.get("type", "").lower() == "application/ld+json":
            self._json_ld = True
            self._json_ld_parts = []
        elif tag == "img":
            self.images.append(values)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self.in_title = False
        elif tag == "script" and self._json_ld:
            self.json_ld_blocks.append("".join(self._json_ld_parts).strip())
            self._json_ld = False
            self._json_ld_parts = []

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self._json_ld:
            self._json_ld_parts.append(data)


def _add(findings: list[Finding], severity: str, code: str, path: str, message: str) -> None:
    findings.append(Finding(severity, code, path, message))


def audit_page(root: Path, relative: str) -> list[Finding]:
    findings: list[Finding] = []
    page = root / relative
    if not page.is_file():
        _add(findings, "error", "PAGE_MISSING", relative, "Indexable page is missing")
        return findings

    parser = SEOParser()
    try:
        parser.feed(page.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive reporting
        _add(findings, "error", "HTML_PARSE", relative, f"Could not parse HTML: {exc}")
        return findings

    title = parser.title
    if not title:
        _add(findings, "error", "TITLE_MISSING", relative, "Missing <title>")
    elif not TITLE_MIN <= len(title) <= TITLE_MAX:
        _add(findings, "warning", "TITLE_LENGTH", relative, f"Title is {len(title)} characters; target {TITLE_MIN}-{TITLE_MAX}")

    description = parser.meta.get("description", "")
    if not description:
        _add(findings, "error", "DESCRIPTION_MISSING", relative, "Missing meta description")
    elif not DESCRIPTION_MIN <= len(description) <= DESCRIPTION_MAX:
        _add(findings, "warning", "DESCRIPTION_LENGTH", relative, f"Description is {len(description)} characters; target {DESCRIPTION_MIN}-{DESCRIPTION_MAX}")

    if parser.h1_count != 1:
        _add(findings, "error", "H1_COUNT", relative, f"Expected exactly one H1; found {parser.h1_count}")

    if len(parser.canonicals) != 1:
        _add(findings, "error", "CANONICAL_COUNT", relative, f"Expected exactly one canonical; found {len(parser.canonicals)}")
    elif not parser.canonicals[0].startswith(f"{PRODUCTION_ORIGIN}/") and parser.canonicals[0] != f"{PRODUCTION_ORIGIN}/":
        _add(findings, "error", "CANONICAL_ORIGIN", relative, f"Canonical must use {PRODUCTION_ORIGIN}")

    for prop in ("og:title", "og:description", "og:type"):
        if not parser.properties.get(prop):
            _add(findings, "warning", "OG_MISSING", relative, f"Missing {prop}")
    if not parser.properties.get("og:url"):
        _add(findings, "warning", "OG_URL_MISSING", relative, "Missing og:url")

    if "keywords" in parser.meta:
        _add(findings, "warning", "META_KEYWORDS", relative, "meta keywords is legacy metadata; do not use it as an SEO control")

    if not parser.json_ld_blocks:
        _add(findings, "warning", "JSON_LD_MISSING", relative, "No JSON-LD block found")
    for block_number, block in enumerate(parser.json_ld_blocks, start=1):
        try:
            json.loads(block)
        except json.JSONDecodeError as exc:
            _add(findings, "error", "JSON_LD_INVALID", relative, f"JSON-LD block {block_number} is invalid: {exc.msg}")

    for index, image in enumerate(parser.images, start=1):
        src = image.get("src", "") or f"image #{index}"
        if "alt" not in image:
            _add(findings, "warning", "IMG_ALT_MISSING", relative, f"Image lacks alt attribute: {src}")
        if not image.get("width") or not image.get("height"):
            _add(findings, "warning", "IMG_DIMENSIONS", relative, f"Image lacks explicit width/height: {src}")

    return findings


def audit_robots(root: Path) -> list[Finding]:
    path = root / "robots.txt"
    relative = "robots.txt"
    findings: list[Finding] = []
    if not path.is_file():
        _add(findings, "error", "ROBOTS_MISSING", relative, "robots.txt is missing")
        return findings
    text = path.read_text(encoding="utf-8")
    expected = f"Sitemap: {PRODUCTION_ORIGIN}/sitemap.xml"
    if expected not in text:
        _add(findings, "error", "ROBOTS_SITEMAP", relative, f"Expected sitemap directive: {expected}")
    if re.search(r"(?im)^\s*disallow\s*:\s*/\s*$", text):
        _add(findings, "error", "ROBOTS_BLOCK_ALL", relative, "robots.txt blocks the entire production site")
    return findings


def audit_sitemap(root: Path, pages: tuple[str, ...]) -> list[Finding]:
    relative = "sitemap.xml"
    path = root / relative
    findings: list[Finding] = []
    if not path.is_file():
        _add(findings, "error", "SITEMAP_MISSING", relative, "sitemap.xml is missing")
        return findings
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        _add(findings, "error", "SITEMAP_XML", relative, f"Invalid XML: {exc}")
        return findings

    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locations = [node.text.strip() for node in tree.findall(".//s:loc", ns) if node.text and node.text.strip()]
    if len(locations) != len(set(locations)):
        _add(findings, "error", "SITEMAP_DUPLICATE", relative, "Sitemap contains duplicate URLs")

    expected_urls = {
        f"{PRODUCTION_ORIGIN}/" if page == "index.html" else f"{PRODUCTION_ORIGIN}/{page}"
        for page in pages
    }
    missing = expected_urls.difference(locations)
    for url in sorted(missing):
        _add(findings, "error", "SITEMAP_PAGE_MISSING", relative, f"Canonical indexable page missing from sitemap: {url}")

    for url in locations:
        parsed = urlsplit(url)
        if f"{parsed.scheme}://{parsed.netloc}" != PRODUCTION_ORIGIN:
            _add(findings, "error", "SITEMAP_ORIGIN", relative, f"Non-production URL in sitemap: {url}")
    if len(locations) <= 2:
        _add(findings, "warning", "SITEMAP_SMALL", relative, f"Sitemap exposes only {len(locations)} URLs; confirm this matches the full canonical production inventory")
    return findings


def audit(root: Path, pages: tuple[str, ...]) -> list[Finding]:
    findings: list[Finding] = []
    for page in pages:
        findings.extend(audit_page(root, page))
    findings.extend(audit_robots(root))
    findings.extend(audit_sitemap(root, pages))
    return sorted(findings, key=lambda item: (0 if item.severity == "error" else 1, item.path, item.code, item.message))


def render_text(findings: list[Finding]) -> None:
    if not findings:
        print("SEO audit: no findings")
        return
    for item in findings:
        print(f"[{item.severity.upper()}] {item.code} {item.path}: {item.message}")
    errors = sum(item.severity == "error" for item in findings)
    warnings = sum(item.severity == "warning" for item in findings)
    print(f"SEO audit summary: {errors} error(s), {warnings} warning(s)")


def render_github(findings: list[Finding]) -> None:
    for item in findings:
        command = "error" if item.severity == "error" else "warning"
        message = item.message.replace("\n", " ").replace("%", "%25").replace("\r", "%0D")
        print(f"::{command} file={item.path},title={item.code}::{message}")
    render_text(findings)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-root", type=Path, default=Path.cwd())
    parser.add_argument("--page", action="append", dest="pages", help="Indexable HTML page relative to site root; repeatable")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when warnings are present")
    parser.add_argument("--format", choices=("text", "json", "github"), default="text")
    args = parser.parse_args(argv)

    root = args.site_root.resolve()
    pages = tuple(args.pages or DEFAULT_INDEXABLE_PAGES)
    findings = audit(root, pages)

    if args.format == "json":
        print(json.dumps([asdict(item) for item in findings], indent=2))
    elif args.format == "github":
        render_github(findings)
    else:
        render_text(findings)

    has_errors = any(item.severity == "error" for item in findings)
    has_warnings = any(item.severity == "warning" for item in findings)
    return 1 if has_errors or (args.strict and has_warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
