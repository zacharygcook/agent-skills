#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("sync_flagship_skills.py")
SPEC = importlib.util.spec_from_file_location("sync_flagship_skills", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load sync_flagship_skills.py")
sync = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = sync
SPEC.loader.exec_module(sync)


def run(*arguments: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(arguments, cwd=cwd, check=False, capture_output=True, text=True)


def initialize_source(root: Path, name: str = "demo-skill", version: str = "1.0.0") -> Path:
    remote = root.parent / f"{root.name}.git"
    run("git", "init", "--bare", str(remote))
    root.mkdir()
    (root / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Demo package.\n---\n\n# Demo\n",
        encoding="utf-8",
    )
    (root / "VERSION").write_text(version + "\n", encoding="utf-8")
    scripts = root / "scripts"
    scripts.mkdir()
    helper = scripts / "helper.sh"
    helper.write_text("#!/usr/bin/env bash\necho ready\n", encoding="utf-8")
    helper.chmod(0o755)
    (root / "skill-package.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "name": name,
                "version_file": "VERSION",
                "mappings": [
                    {"source": "SKILL.md", "target": "SKILL.md"},
                    {"source": "VERSION", "target": "VERSION"},
                    {"source": "scripts", "target": "scripts"},
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    for command in (
        ("git", "init", "-b", "master"),
        ("git", "config", "user.name", "Sync Test"),
        ("git", "config", "user.email", "sync@example.com"),
        ("git", "remote", "add", "origin", str(remote)),
        ("git", "add", "SKILL.md", "VERSION", "scripts/helper.sh", "skill-package.json"),
        ("git", "commit", "-m", "Create canonical package"),
        ("git", "push", "-u", "origin", "master"),
    ):
        result = run(*command, cwd=root)
        if result.returncode != 0:
            raise RuntimeError(result.stderr)
    return root


class FlagshipSyncTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.collection = self.root / "collection"
        (self.collection / "skills").mkdir(parents=True)
        (self.collection / "scripts").mkdir()
        self.lock = self.collection / "flagship-skills.lock.json"
        self.lock.write_text('{"schema_version":1,"packages":{}}\n', encoding="utf-8")
        self.originals = (sync.REPO_ROOT, sync.SKILLS_ROOT, sync.LOCK_PATH)
        sync.REPO_ROOT = self.collection
        sync.SKILLS_ROOT = self.collection / "skills"
        sync.LOCK_PATH = self.lock

    def tearDown(self) -> None:
        sync.REPO_ROOT, sync.SKILLS_ROOT, sync.LOCK_PATH = self.originals
        self.temporary.cleanup()

    def test_preview_apply_and_drift_detection(self) -> None:
        source = initialize_source(self.root / "source")
        preview = sync.update_package("demo-skill", source, False)
        self.assertTrue(preview["changed"])
        self.assertFalse((sync.SKILLS_ROOT / "demo-skill").exists())
        applied = sync.update_package("demo-skill", source, True)
        self.assertTrue(applied["applied"])
        self.assertTrue(sync.check_all()["ok"])
        helper = sync.SKILLS_ROOT / "demo-skill" / "scripts" / "helper.sh"
        self.assertTrue(os.access(helper, os.X_OK))
        helper.write_text("drift\n", encoding="utf-8")
        report = sync.check_all()
        self.assertFalse(report["ok"])
        self.assertEqual(report["packages"][0]["differences"]["changed"], ["scripts/helper.sh"])

    def test_update_deletes_removed_files_and_requires_version_bump(self) -> None:
        source = initialize_source(self.root / "source")
        sync.update_package("demo-skill", source, True)
        (source / "scripts" / "helper.sh").unlink()
        run("git", "add", "-u", cwd=source)
        run("git", "commit", "-m", "Remove helper", cwd=source)
        run("git", "push", cwd=source)
        with self.assertRaisesRegex(sync.SyncError, "without a version bump"):
            sync.update_package("demo-skill", source, True)
        (source / "VERSION").write_text("1.1.0\n", encoding="utf-8")
        run("git", "add", "VERSION", cwd=source)
        run("git", "commit", "-m", "Release 1.1.0", cwd=source)
        run("git", "push", cwd=source)
        sync.update_package("demo-skill", source, True)
        self.assertFalse((sync.SKILLS_ROOT / "demo-skill" / "scripts" / "helper.sh").exists())

    def test_dirty_and_unpushed_sources_are_rejected(self) -> None:
        source = initialize_source(self.root / "source")
        (source / "SKILL.md").write_text("dirty\n", encoding="utf-8")
        with self.assertRaisesRegex(sync.SyncError, "uncommitted"):
            sync.update_package("demo-skill", source, False)
        run("git", "checkout", "--", "SKILL.md", cwd=source)
        (source / "VERSION").write_text("1.1.0\n", encoding="utf-8")
        run("git", "add", "VERSION", cwd=source)
        run("git", "commit", "-m", "Unpushed release", cwd=source)
        with self.assertRaisesRegex(sync.SyncError, "not pushed"):
            sync.update_package("demo-skill", source, False)

    def test_symlink_escape_is_rejected(self) -> None:
        source = initialize_source(self.root / "source")
        outside = self.root / "outside.txt"
        outside.write_text("private\n", encoding="utf-8")
        (source / "scripts" / "escape").symlink_to(outside)
        run("git", "add", "scripts/escape", cwd=source)
        run("git", "commit", "-m", "Add escaping link", cwd=source)
        run("git", "push", cwd=source)
        with self.assertRaisesRegex(sync.SyncError, "Symlink escapes"):
            sync.update_package("demo-skill", source, False)


if __name__ == "__main__":
    unittest.main()
