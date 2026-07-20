"""Command-line agent for ClearGlass Financial Influence Watchdog."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .entity_extractor import LLMEntityExtractor


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="clearglass-watchdog",
        description="Extract auditable financial-influence entities from Canadian governance documents.",
    )
    parser.add_argument("input", nargs="?", help="UTF-8 document path. Reads stdin when omitted.")
    parser.add_argument("--output", "-o", help="Write JSON result to this path instead of stdout.")
    parser.add_argument("--document-id")
    parser.add_argument("--title")
    parser.add_argument("--source-type", default="council_minutes")
    parser.add_argument("--jurisdiction", default="Ontario")
    parser.add_argument("--provider", choices=("auto", "openai", "anthropic", "compatible"), default="auto")
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--base-url")
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument(
        "--allow-dev-fallback",
        action="store_true",
        help="Allow deterministic regex fallback. Never use this flag for production evidence.",
    )
    parser.add_argument(
        "--allow-ungrounded",
        action="store_true",
        help="Flag rather than drop ungrounded model entities. Not recommended.",
    )
    return parser


def _read_input(path: str | None) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8")
    if sys.stdin.isatty():
        raise ValueError("Provide an input file or pipe document text through stdin")
    return sys.stdin.read()


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        text = _read_input(args.input)
        metadata: dict[str, Any] = {
            "title": args.title or args.document_id or (Path(args.input).name if args.input else "stdin"),
            "source_type": args.source_type,
            "jurisdiction": args.jurisdiction,
        }
        extractor = LLMEntityExtractor(
            model_name=args.model,
            provider=args.provider,
            base_url=args.base_url,
            max_retries=args.max_retries,
            enable_local_fallback=args.allow_dev_fallback,
            strict_grounding=not args.allow_ungrounded,
        )
        result = extractor.extract(text, document_id=args.document_id, metadata=metadata)
        rendered = json.dumps(result.model_dump(mode="json"), indent=2, ensure_ascii=False)
        if args.output:
            Path(args.output).write_text(rendered + "\n", encoding="utf-8")
        else:
            print(rendered)
        return 0
    except Exception as exc:
        print(f"clearglass-watchdog: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
