#!/usr/bin/env python3
"""Validate the collected skill packages without external dependencies."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
COLLECTION_ROOTS = ("skills",)
PROHIBITED_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".pyc"}
PROHIBITED_NAMES = {".env", "credentials.json", "service-account.json"}
FORMER_COMPANY_SPECIFIC_PATTERNS = (
    re.compile(r"linkedin-messaging", re.IGNORECASE),
    re.compile(r"tex aesthetic", re.IGNORECASE),
    re.compile(r"zacharycooktex", re.IGNORECASE),
    re.compile(r"github-tex", re.IGNORECASE),
)


def skill_directories() -> list[Path]:
    return sorted(skill_file.parent for skill_file in (ROOT / "skills").glob("*/SKILL.md"))


def frontmatter(skill_file: Path) -> dict[str, str]:
    text = skill_file.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}
    values: dict[str, str] = {}
    for line in lines[1:end]:
        match = re.match(r"^(name|description):\s*(.*)$", line)
        if match:
            values[match.group(1)] = match.group(2).strip()
    return values


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


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    skills = skill_directories()
    hashes: dict[str, list[Path]] = defaultdict(list)

    for directory in skills:
        skill_file = directory / "SKILL.md"
        metadata = frontmatter(skill_file)
        relative = directory.relative_to(ROOT)
        if not metadata.get("name"):
            errors.append(f"{relative}: missing name frontmatter")
        if not metadata.get("description"):
            errors.append(f"{relative}: missing description frontmatter")
        if metadata.get("name") and metadata["name"].strip('"') != directory.name:
            errors.append(
                f"{relative}: frontmatter name {metadata['name']} does not match directory"
            )
        if skill_file.read_text(encoding="utf-8").count("\n---\n") < 1:
            errors.append(f"{relative}: malformed YAML frontmatter")
        hashes[tree_hash(directory)].append(relative)

        for path in directory.rglob("*"):
            if not path.is_file():
                continue
            if path.name in PROHIBITED_NAMES or path.suffix.lower() in PROHIBITED_SUFFIXES:
                errors.append(f"{path.relative_to(ROOT)}: prohibited credential/cache file")
            if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".woff", ".woff2"}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for pattern in FORMER_COMPANY_SPECIFIC_PATTERNS:
                if pattern.search(text):
                    errors.append(
                        f"{path.relative_to(ROOT)}: contains excluded former-company-specific content"
                    )
                    break
            if re.search(r"/(Users/[^/]+|home/[^/]+)/", text):
                errors.append(f"{path.relative_to(ROOT)}: contains a machine-specific path")

        openai_metadata = directory / "agents" / "openai.yaml"
        if not openai_metadata.exists():
            warnings.append(f"{relative}: missing agents/openai.yaml")
        else:
            openai_text = openai_metadata.read_text(encoding="utf-8")
            if f"${directory.name}" not in openai_text:
                errors.append(
                    f"{openai_metadata.relative_to(ROOT)}: default prompt must mention ${directory.name}"
                )

    duplicates = [paths for paths in hashes.values() if len(paths) > 1]
    for paths in duplicates:
        warnings.append("duplicate skill trees: " + ", ".join(map(str, paths)))

    rubric = ROOT / "skills" / "agent-readiness" / "references" / "rubric.json"
    if rubric.exists():
        rubric_data = json.loads(rubric.read_text(encoding="utf-8"))
        ids = [criterion["id"] for criterion in rubric_data.get("criteria", [])]
        if len(ids) != 82 or len(set(ids)) != 82:
            errors.append("agent-readiness rubric must contain 82 unique criteria")

    onboarding_catalog = (
        ROOT / "skills" / "setup-agent-skills" / "references" / "catalog.json"
    )
    if onboarding_catalog.exists():
        catalog_data = json.loads(onboarding_catalog.read_text(encoding="utf-8"))
        catalog_skills = set(catalog_data.get("skills", {}))
        package_skills = {directory.name for directory in skills}
        if catalog_skills != package_skills:
            missing = sorted(package_skills - catalog_skills)
            extra = sorted(catalog_skills - package_skills)
            errors.append(
                "onboarding catalog must match skill packages "
                f"(missing={missing}, extra={extra})"
            )

    print(
        f"Validated {len(skills)} skills: "
        f"{len(skills)} reusable."
    )
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
