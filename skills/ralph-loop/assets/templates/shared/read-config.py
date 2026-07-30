#!/usr/bin/env python3
"""Read one value from Ralph's data-only configuration format."""

from __future__ import annotations

import re
import shlex
import sys
from pathlib import Path


KEY = re.compile(r"^[A-Z][A-Z0-9_]*$")
MAX_CONFIG_BYTES = 128 * 1024


def load(path: Path) -> dict[str, str]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"config must be a regular file, not a symlink: {path}")
    if path.stat().st_size > MAX_CONFIG_BYTES:
        raise ValueError(f"config exceeds {MAX_CONFIG_BYTES} bytes: {path}")

    values: dict[str, str] = {}
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line or line.lstrip().startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"{path}:{line_number}: expected KEY=VALUE")
        key, raw_value = line.split("=", 1)
        if not KEY.fullmatch(key):
            raise ValueError(f"{path}:{line_number}: invalid key {key!r}")
        if key in values:
            raise ValueError(f"{path}:{line_number}: duplicate key {key}")
        parsed = shlex.split(raw_value, comments=False, posix=True)
        if len(parsed) > 1:
            raise ValueError(
                f"{path}:{line_number}: values with spaces must use shell quoting"
            )
        values[key] = parsed[0] if parsed else ""
    return values


def main() -> int:
    if len(sys.argv) != 3 or not KEY.fullmatch(sys.argv[2]):
        print("usage: read-config.py <config.env> <KEY>", file=sys.stderr)
        return 2
    try:
        values = load(Path(sys.argv[1]))
    except (OSError, UnicodeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    sys.stdout.write(values.get(sys.argv[2], ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
