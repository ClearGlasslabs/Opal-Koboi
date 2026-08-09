"""Fail-closed validation for the GitHub Pages release artifact."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

PRODUCTION_ORIGIN = "https://www.clearglassinc.com"
PUBLISHED_FILES = {
    "index.html",
    "CG-os.html",
    "404.html",
    "artemis-blueprint.md",
    "robots.txt",
    "sitemap.xml",
    "docs/advanced-campaign-system.md",
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.duplicate_ids: set[str] = set()
        self.references: list[tuple[str, str]] = []
        self.canonicals: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if value := values.get("id"):
            if value in self.ids:
                self.duplicate_ids.add(value)
            self.ids.add(value)
        for attribute in ("href", "src"):
            if (value := values.get(attribute)) is not None:
                self.references.append((attribute, value))
        if tag == "link" and values.get("rel") == "canonical" and values.get("href"):
            self.canonicals.append(values["href"] or "")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for relative in sorted(PUBLISHED_FILES):
        if not (root / relative).is_file():
            errors.append(f"published file is missing: {relative}")
    for relative in ("index.html", "CG-os.html", "404.html"):
        page = root / relative
        if not page.is_file():
            continue
        parser = PageParser()
        parser.feed(page.read_text(encoding="utf-8"))
        for duplicate_id in sorted(parser.duplicate_ids):
            errors.append(f"{relative}: duplicate id: {duplicate_id}")
        if len(parser.canonicals) != 1 or not parser.canonicals[0].startswith(PRODUCTION_ORIGIN):
            errors.append(f"{relative}: expected exactly one production canonical URL")
        for attribute, reference in parser.references:
            if not reference.strip() or (attribute == "href" and reference == "#"):
                errors.append(f"{relative}: empty {attribute} target")
                continue
            parsed = urlsplit(reference)
            if parsed.scheme or reference.startswith(("mailto:", "tel:", "//")):
                continue
            if parsed.path:
                target = unquote(parsed.path.lstrip("/"))
                if target not in PUBLISHED_FILES and not target.startswith("assets/"):
                    errors.append(f"{relative}: unpublished {attribute} target: {reference}")
                elif not (root / target).is_file():
                    errors.append(f"{relative}: missing {attribute} target: {reference}")
            if parsed.fragment and not parsed.path and parsed.fragment not in parser.ids:
                errors.append(f"{relative}: missing fragment target: #{parsed.fragment}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    errors = validate(args.site_root.resolve())
    if errors:
        print("Static-site validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("Static-site validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
