#!/usr/bin/env python3
"""Synchronize canonical flagship skill packages into this collection."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = REPO_ROOT / "skills"
LOCK_PATH = REPO_ROOT / "flagship-skills.lock.json"
IGNORED_NAMES = {".DS_Store", "__pycache__"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}


class SyncError(ValueError):
    pass


def run_git(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SyncError(result.stderr.strip() or "Git command failed")
    return result.stdout.strip()


def safe_relative(raw: str, label: str) -> Path:
    path = Path(raw)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise SyncError(f"Unsafe {label} path: {raw}")
    return path


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SyncError(f"Cannot read {path}: {error}") from error
    if not isinstance(value, dict):
        raise SyncError(f"Expected an object in {path}")
    return value


def load_lock() -> dict[str, Any]:
    if not LOCK_PATH.exists():
        return {"schema_version": 1, "packages": {}}
    lock = load_json(LOCK_PATH)
    if lock.get("schema_version") != 1 or not isinstance(lock.get("packages"), dict):
        raise SyncError("Unsupported flagship-skills.lock.json schema")
    return lock


def write_lock(lock: dict[str, Any]) -> None:
    temporary = LOCK_PATH.with_name(f".{LOCK_PATH.name}.tmp")
    temporary.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(LOCK_PATH)


def ignored(path: Path) -> bool:
    return any(part in IGNORED_NAMES for part in path.parts) or path.suffix in IGNORED_SUFFIXES


def validate_source_link(path: Path, source_root: Path) -> None:
    if not path.is_symlink():
        return
    try:
        path.resolve(strict=True).relative_to(source_root.resolve())
    except (OSError, ValueError) as error:
        raise SyncError(f"Symlink escapes canonical source: {path}") from error


def copy_entry(source: Path, target: Path, source_root: Path) -> None:
    validate_source_link(source, source_root)
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.is_symlink():
        target.symlink_to(os.readlink(source))
        return
    if source.is_file():
        shutil.copy2(source, target)
        return
    if not source.is_dir():
        raise SyncError(f"Unsupported package source entry: {source}")
    target.mkdir(parents=True, exist_ok=True)
    for child in sorted(source.iterdir(), key=lambda item: item.name):
        if ignored(child.relative_to(source_root)):
            continue
        copy_entry(child, target / child.name, source_root)


def load_manifest(source_root: Path) -> dict[str, Any]:
    manifest_path = source_root / "skill-package.json"
    manifest = load_json(manifest_path)
    if manifest.get("schema_version") != 1:
        raise SyncError(f"Unsupported package manifest schema: {manifest_path}")
    name = manifest.get("name")
    mappings = manifest.get("mappings")
    if not isinstance(name, str) or not name or not isinstance(mappings, list) or not mappings:
        raise SyncError(f"Invalid package manifest: {manifest_path}")
    targets: list[Path] = []
    for mapping in mappings:
        if not isinstance(mapping, dict):
            raise SyncError("Every package mapping must be an object")
        source = safe_relative(str(mapping.get("source", "")), "source")
        target = safe_relative(str(mapping.get("target", "")), "target")
        if not (source_root / source).exists() and not (source_root / source).is_symlink():
            raise SyncError(f"Missing canonical package source: {source}")
        for existing in targets:
            if target == existing or target.is_relative_to(existing) or existing.is_relative_to(target):
                raise SyncError(f"Overlapping package targets: {existing} and {target}")
        targets.append(target)
    return manifest


def export_package(source_root: Path, destination: Path) -> dict[str, Any]:
    manifest = load_manifest(source_root)
    for mapping in manifest["mappings"]:
        source = source_root / safe_relative(mapping["source"], "source")
        target = destination / safe_relative(mapping["target"], "target")
        copy_entry(source, target, source_root)
    if not (destination / "SKILL.md").is_file():
        raise SyncError("Exported package is missing SKILL.md")
    return manifest


def tree_state(root: Path) -> dict[str, dict[str, Any]]:
    state: dict[str, dict[str, Any]] = {}
    if not root.exists():
        return state
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if ignored(relative) or path.is_dir():
            continue
        key = relative.as_posix()
        if path.is_symlink():
            state[key] = {"kind": "symlink", "target": os.readlink(path)}
        else:
            mode = path.stat().st_mode
            state[key] = {
                "kind": "file",
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "executable": bool(mode & stat.S_IXUSR),
            }
    return state


def fingerprint(state: dict[str, dict[str, Any]]) -> str:
    payload = json.dumps(state, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


def diff_states(current: dict[str, Any], expected: dict[str, Any]) -> dict[str, list[str]]:
    current_keys = set(current)
    expected_keys = set(expected)
    return {
        "added": sorted(expected_keys - current_keys),
        "removed": sorted(current_keys - expected_keys),
        "changed": sorted(key for key in current_keys & expected_keys if current[key] != expected[key]),
    }


def source_metadata(source_root: Path, manifest: dict[str, Any]) -> dict[str, str]:
    if run_git(source_root, "status", "--porcelain"):
        raise SyncError(f"Canonical source has uncommitted changes: {source_root}")
    head = run_git(source_root, "rev-parse", "HEAD")
    remote_head = run_git(source_root, "rev-parse", "origin/master")
    if head != remote_head:
        raise SyncError(f"Canonical source HEAD is not pushed to origin/master: {source_root}")
    remote = run_git(source_root, "remote", "get-url", "origin")
    version_path = source_root / safe_relative(str(manifest.get("version_file", "VERSION")), "version")
    version = version_path.read_text(encoding="utf-8").strip()
    if not version or any(character.isspace() for character in version):
        raise SyncError(f"Invalid package version: {version_path}")
    return {"commit": head, "repository": remote, "version": version}


def check_package(name: str, entry: dict[str, Any]) -> dict[str, Any]:
    target = SKILLS_ROOT / name
    current = tree_state(target)
    expected = entry.get("files")
    if not isinstance(expected, dict):
        raise SyncError(f"Lock entry has no file state: {name}")
    differences = diff_states(current, expected)
    actual_fingerprint = fingerprint(current)
    ok = actual_fingerprint == entry.get("fingerprint") and not any(differences.values())
    return {
        "skill": name,
        "ok": ok,
        "version": entry.get("version"),
        "source_commit": entry.get("source_commit"),
        "fingerprint": actual_fingerprint,
        "differences": differences,
    }


def check_all(skill: str | None = None) -> dict[str, Any]:
    lock = load_lock()
    packages = lock["packages"]
    names = [skill] if skill else sorted(packages)
    if not names:
        raise SyncError("No flagship packages are locked")
    missing = [name for name in names if name not in packages]
    if missing:
        raise SyncError("Unknown locked flagship skill: " + ", ".join(missing))
    results = [check_package(name, packages[name]) for name in names]
    return {"ok": all(item["ok"] for item in results), "packages": results}


def update_package(skill: str, source_root: Path, apply: bool) -> dict[str, Any]:
    source_root = source_root.resolve()
    with tempfile.TemporaryDirectory(prefix=f"flagship-{skill}-") as directory:
        exported = Path(directory) / skill
        exported.mkdir()
        manifest = export_package(source_root, exported)
        if manifest["name"] != skill:
            raise SyncError(f"Manifest skill {manifest['name']} does not match requested {skill}")
        metadata = source_metadata(source_root, manifest)
        expected = tree_state(exported)
        expected_fingerprint = fingerprint(expected)
        current = tree_state(SKILLS_ROOT / skill)
        differences = diff_states(current, expected)
        lock = load_lock()
        previous = lock["packages"].get(skill)
        changed = any(differences.values())
        if previous and changed and previous.get("version") == metadata["version"]:
            raise SyncError(
                f"Distributable files changed without a version bump for {skill} ({metadata['version']})"
            )
        result = {
            "skill": skill,
            "applied": apply,
            "changed": changed,
            "version": metadata["version"],
            "source_commit": metadata["commit"],
            "fingerprint": expected_fingerprint,
            "differences": differences,
        }
        if not apply:
            return result
        target = SKILLS_ROOT / skill
        if target.is_symlink():
            raise SyncError(f"Refusing symlinked collection target: {target}")
        temporary_target = SKILLS_ROOT / f".{skill}.sync-tmp"
        if temporary_target.exists():
            shutil.rmtree(temporary_target)
        shutil.copytree(exported, temporary_target, symlinks=True)
        if target.exists():
            shutil.rmtree(target)
        temporary_target.replace(target)
        lock["packages"][skill] = {
            "source_repository": metadata["repository"],
            "source_commit": metadata["commit"],
            "version": metadata["version"],
            "fingerprint": expected_fingerprint,
            "files": expected,
        }
        write_lock(lock)
        verification = check_package(skill, lock["packages"][skill])
        if not verification["ok"]:
            raise SyncError(f"Post-sync verification failed for {skill}")
        return result


def print_result(result: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    if "packages" in result:
        for package in result["packages"]:
            status = "CURRENT" if package["ok"] else "DRIFT"
            print(f"{status:7} {package['skill']} {package.get('version') or 'unknown'} {str(package.get('source_commit'))[:12]}")
            for category, paths in package["differences"].items():
                for path in paths:
                    print(f"  {category}: {path}")
        return
    action = "applied" if result["applied"] else "preview"
    print(f"{action}: {result['skill']} {result['version']} from {result['source_commit'][:12]}")
    for category, paths in result["differences"].items():
        for path in paths:
            print(f"  {category}: {path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check", help="Verify collection packages against the lockfile.")
    check.add_argument("--skill")
    check.add_argument("--json", action="store_true")
    update = subparsers.add_parser("update", help="Preview or apply a canonical package export.")
    update.add_argument("--skill", required=True)
    update.add_argument("--source-root", type=Path, required=True)
    update.add_argument("--apply", action="store_true")
    update.add_argument("--json", action="store_true")
    return parser


def main() -> int:
    arguments = build_parser().parse_args()
    try:
        if arguments.command == "check":
            result = check_all(arguments.skill)
            print_result(result, arguments.json)
            return 0 if result["ok"] else 1
        result = update_package(arguments.skill, arguments.source_root, arguments.apply)
        print_result(result, arguments.json)
        return 0
    except (OSError, SyncError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
