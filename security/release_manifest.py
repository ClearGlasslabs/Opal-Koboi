#!/usr/bin/env python3
"""Create a deterministic SHA-256 manifest of tracked release inputs."""

from __future__ import annotations

import argparse
import hashlib
import subprocess  # nosec B404 - fixed executable/argv; shell execution is never used.
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="SHA256SUMS")
    args = parser.parse_args()
    output = Path(args.output)
    tracked = subprocess.run(  # nosec B603,B607 - constant git command with shell=False.
        ["git", "ls-files", "-z"], check=True, capture_output=True
    ).stdout.split(b"\0")
    lines = []
    for raw in sorted(filter(None, tracked)):
        path = Path(raw.decode())
        if path == output or not path.is_file():
            continue
        lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.as_posix()}")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
