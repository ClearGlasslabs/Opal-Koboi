#!/usr/bin/env python3
"""Create a deterministic SHA-256 manifest of tracked release inputs."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess  # nosec B404
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="SHA256SUMS")
    args = parser.parse_args()
    output = Path(args.output)
    git_path = shutil.which("git")
    if git_path is None:
        raise RuntimeError("git executable not found")
    # The executable is resolved from PATH and every argument is constant; shell execution is not used.
    tracked = subprocess.run(  # nosec B603
        [git_path, "ls-files", "-z"], check=True, capture_output=True
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
