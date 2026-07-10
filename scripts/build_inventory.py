#!/usr/bin/env python3
"""Generate a deterministic inventory of collected skill packages."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "inventory" / "skills.json"


def tree_hash(directory: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in directory.rglob("*") if item.is_file()):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        digest.update(str(path.relative_to(directory)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def build_inventory() -> dict[str, object]:
    entries = []
    for collection in ("skills",):
        for skill_file in sorted((ROOT / collection).glob("*/SKILL.md")):
            directory = skill_file.parent
            relative = directory.relative_to(ROOT)
            files = [
                path
                for path in directory.rglob("*")
                if path.is_file()
                and ".git" not in path.parts
                and "__pycache__" not in path.parts
            ]
            entries.append(
                {
                    "name": directory.name,
                    "path": str(relative),
                    "classification": collection,
                    "source": "curated",
                    "file_count": len(files),
                    "bytes": sum(path.stat().st_size for path in files),
                    "sha256": tree_hash(directory),
                }
            )
    return {
        "schema_version": "1.0",
        "skill_count": len(entries),
        "skills": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    rendered = f"{json.dumps(build_inventory(), indent=2)}\n"
    if arguments.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            print("inventory/skills.json is stale; run python3 scripts/build_inventory.py")
            return 1
        print("Skill inventory is current.")
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
