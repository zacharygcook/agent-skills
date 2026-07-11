#!/usr/bin/env python3
"""Tests for the setup-agent-skills onboarding doctor."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("doctor.py")
SPEC = importlib.util.spec_from_file_location("setup_agent_skills_doctor", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load doctor.py")
doctor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(doctor)


class DoctorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = doctor.load_catalog()

    def write(self, root: Path, relative: str, content: str = "") -> Path:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def make_executable(self, root: Path, name: str) -> Path:
        path = self.write(root, name, "#!/bin/sh\nexit 0\n")
        path.chmod(0o755)
        return path

    def empty_machine(self) -> dict[str, object]:
        return {
            "os": "linux",
            "os_name": "Linux",
            "distribution": "Test Linux",
            "architecture": "x86_64",
            "python": "3.12.0",
            "home": "/tmp/home",
            "commands": {name: None for name in doctor.COMMAND_NAMES},
            "package_managers": [],
            "agents": [],
        }

    def test_catalog_defines_seven_packs_and_all_twenty_skills(self) -> None:
        self.assertEqual(len(self.catalog["packs"]), 7)
        self.assertEqual(len(self.catalog["skills"]), 20)
        self.assertIn("setup-agent-skills", self.catalog["skills"])
        self.assertIn("agent-readiness-scoring", self.catalog["skills"])
        self.assertIn("write-public-readme", self.catalog["skills"])
        self.assertIn("design-human-first-cli", self.catalog["skills"])

    def test_fingerprint_detects_web_postgres_queue_and_review_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".git").mkdir()
            self.write(
                root, ".github/workflows/automated-review.yml", "name: AI review"
            )
            self.write(
                root,
                "package.json",
                json.dumps(
                    {
                        "bin": {"fixture": "bin/fixture.js"},
                        "dependencies": {"next": "1", "pg": "1"},
                        "devDependencies": {"@playwright/test": "1", "knip": "1"},
                    }
                ),
            )
            self.write(root, "tsconfig.json", "{}")
            self.write(root, "README.md", "# Public fixture")
            self.write(root, "bin/fixture.js", "console.log('fixture')")
            self.write(root, "playwright.config.ts", "export default {}")
            self.write(
                root,
                "src/queue_worker.ts",
                "SELECT * FROM queue_jobs FOR UPDATE SKIP LOCKED",
            )
            self.write(root, "tests/home.spec.ts", "test('home', () => {})")
            self.write(root, "scripts/backfill_contacts.py", "print('dry run')")
            for index in range(3):
                self.write(root, f"docs/page-{index}.md", "# Docs")

            result = doctor.fingerprint_repository(root)
            signals = result["signals"]
            for expected in (
                "automated_review",
                "browser_e2e",
                "cli",
                "docs_heavy",
                "frontend",
                "git",
                "github",
                "knip",
                "live_scripts",
                "postgres",
                "queue",
                "readme",
                "tests",
                "typescript",
                "web",
            ):
                self.assertIn(expected, signals)

    def test_skill_names_containing_test_or_spec_do_not_fake_test_signal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "skills/good-test-bad-test/SKILL.md", "# Test guidance")
            self.write(root, "references/spec-breakdown.md", "# Spec")
            result = doctor.fingerprint_repository(root)
            self.assertNotIn("tests", result["signals"])

    def test_agent_detection_separates_active_command_and_config_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            bin_dir = root / "bin"
            (home / ".codex").mkdir(parents=True)
            (home / ".claude").mkdir(parents=True)
            self.make_executable(bin_dir, "codex")
            self.make_executable(bin_dir, "claude")
            env = {"PATH": str(bin_dir), "CODEX_THREAD_ID": "test-thread"}
            machine = doctor.detect_machine(home, env, root, str(bin_dir))
            agents = {item["id"]: item for item in machine["agents"]}
            self.assertEqual(agents["codex"]["status"], "active")
            self.assertEqual(agents["codex"]["confidence"], "high")
            self.assertEqual(agents["claude-code"]["status"], "installed")
            self.assertEqual(agents["claude-code"]["confidence"], "high")

    def test_config_only_agent_is_low_confidence_not_missing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            (home / ".factory").mkdir(parents=True)
            machine = doctor.detect_machine(home, {"PATH": ""}, root, "")
            agents = {item["id"]: item for item in machine["agents"]}
            self.assertEqual(agents["droid"]["status"], "configured")
            self.assertEqual(agents["droid"]["confidence"], "low")

    def test_installed_skills_are_separated_by_project_and_global_scope(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "repo"
            home = root / "home"
            (repo / ".agents/skills/agent-readiness-scoring").mkdir(parents=True)
            (home / ".agents/skills/repo-cleanup-auditor").mkdir(parents=True)
            installed = doctor.installed_skills(self.catalog, repo, home, {})
            self.assertIn("agent-readiness-scoring", installed["project"])
            self.assertNotIn("agent-readiness-scoring", installed["global"])
            self.assertIn("repo-cleanup-auditor", installed["global"])
            self.assertNotIn("repo-cleanup-auditor", installed["project"])

    def test_prerequisite_statuses_distinguish_required_provider_and_fallback(
        self,
    ) -> None:
        machine = self.empty_machine()
        home = Path(machine["home"])
        readiness = self.catalog["skills"]["agent-readiness-scoring"]
        mermaid = self.catalog["skills"]["mermaid-diagrams"]
        perplexity = self.catalog["skills"]["perplexity-research"]
        self.assertEqual(
            doctor.evaluate_prerequisites(
                readiness["prerequisites"], machine, home, {}
            )[0],
            "needs_setup",
        )
        self.assertEqual(
            doctor.evaluate_prerequisites(mermaid["prerequisites"], machine, home, {})[
                0
            ],
            "ready_with_fallbacks",
        )
        self.assertEqual(
            doctor.evaluate_prerequisites(
                perplexity["prerequisites"], machine, home, {}
            )[0],
            "needs_provider",
        )

    def test_pack_recommends_skills_without_repository_signals(self) -> None:
        machine = self.empty_machine()
        machine["commands"]["python3"] = "/test/python3"
        repository = {"signals": {"always": ["setup baseline"]}}
        recommendations = doctor.recommend_skills(
            self.catalog,
            repository,
            machine,
            {},
            ["typescript-hygiene"],
            [],
            Path(machine["home"]),
            {},
        )
        names = {item["name"] for item in recommendations}
        self.assertTrue(
            {
                "setup-agent-skills",
                "agent-readiness-scoring",
                "repo-cleanup-auditor",
            }.issubset(names)
        )
        self.assertTrue(
            {
                "ban-type-assertions",
                "fix-knip-unused-exports",
                "ui-css-performance",
            }.issubset(names)
        )

    def test_project_plan_does_not_treat_global_install_as_vendored(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "repo"
            home = root / "home"
            repo.mkdir()
            (repo / ".git").mkdir()
            (home / ".agents/skills/agent-readiness-scoring").mkdir(parents=True)
            bin_dir = root / "bin"
            self.make_executable(bin_dir, "python3")
            self.make_executable(bin_dir, "npx")
            report = doctor.build_report(
                repo,
                self.catalog,
                [],
                [],
                [],
                False,
                home,
                {"PATH": str(bin_dir)},
                str(bin_dir),
            )
            self.assertIn("agent-readiness-scoring", report["install_plan"]["skills"])
            self.assertIn(
                "agent-readiness-scoring", report["installed_skills"]["global"]
            )

    def test_install_argv_is_explicit_copy_mode_and_scope_aware(self) -> None:
        project = doctor.build_install_argv(
            "owner/repo", ["one", "two"], ["codex", "claude-code"], False
        )
        self.assertEqual(
            project[:5], ["npx", "skills@latest", "add", "owner/repo", "--skill"]
        )
        self.assertIn("--copy", project)
        self.assertNotIn("--global", project)
        self.assertEqual(project[-1], "-y")
        global_plan = doctor.build_install_argv("owner/repo", ["one"], [], True)
        self.assertIn("--global", global_plan)
        self.assertNotIn("-y", global_plan)

    def test_explicit_skill_selection_limits_the_install_plan(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "repo"
            home = root / "home"
            bin_dir = root / "bin"
            repo.mkdir()
            self.make_executable(bin_dir, "python3")
            self.make_executable(bin_dir, "npx")
            report = doctor.build_report(
                repo,
                self.catalog,
                [],
                ["agent-readiness-scoring"],
                ["codex"],
                False,
                home,
                {"PATH": str(bin_dir)},
                str(bin_dir),
            )
            self.assertEqual(
                report["install_plan"]["skills"], ["agent-readiness-scoring"]
            )
            self.assertIn("--agent codex -y", report["install_plan"]["command"])

    def test_cli_json_is_clean_room_safe_and_does_not_read_dotenv_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "repo"
            home = root / "home"
            bin_dir = root / "bin"
            repo.mkdir()
            home.mkdir()
            self.make_executable(bin_dir, "python3")
            self.make_executable(bin_dir, "npx")
            self.write(repo, ".env", "SUPER_SECRET_VALUE=never-print-this")
            self.write(repo, "package.json", '{"devDependencies":{"typescript":"1"}}')
            self.write(repo, "tsconfig.json", "{}")
            env = {"HOME": str(home), "PATH": str(bin_dir)}
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--repo",
                    str(repo),
                    "--format",
                    "json",
                    "--pack",
                    "typescript-hygiene",
                ],
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertNotIn("never-print-this", completed.stdout)
            report = json.loads(completed.stdout)
            names = {item["name"] for item in report["recommendations"]}
            self.assertIn("ban-type-assertions", names)
            self.assertIn("setup-agent-skills", report["install_plan"]["skills"])

    def test_cli_refuses_install_without_explicit_yes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo", directory, "--install"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 2)
            self.assertIn("--install requires --yes", completed.stderr)
            self.assertFalse((Path(directory) / ".agents").exists())

    def test_cli_refuses_unattended_install_without_agent_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--repo",
                    directory,
                    "--install",
                    "--yes",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 2)
            self.assertIn("at least one explicit --agent", completed.stderr)
            self.assertFalse((Path(directory) / ".agents").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
