#!/usr/bin/env python3
"""Inspect a machine and repository, then recommend and optionally vendor agent skills."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = SKILL_ROOT / "references" / "catalog.json"
IGNORED_DIRECTORIES = {
    ".git",
    ".hg",
    ".next",
    ".nuxt",
    ".pytest_cache",
    ".tox",
    ".venv",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
    "venv",
}
TEXT_MANIFEST_NAMES = {
    "Cargo.toml",
    "Gemfile",
    "go.mod",
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "composer.json",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
}
SOURCE_SUFFIXES = {
    ".c",
    ".cpp",
    ".cs",
    ".css",
    ".go",
    ".html",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".md",
    ".mjs",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".sh",
    ".sql",
    ".svelte",
    ".swift",
    ".ts",
    ".tsx",
    ".vue",
}
COMMAND_NAMES = {
    "amp",
    "apt-get",
    "brew",
    "choco",
    "claude",
    "chromium",
    "chromium-browser",
    "chrome",
    "codex",
    "copilot",
    "dnf",
    "droid",
    "factory",
    "gemini",
    "gh",
    "git",
    "gitleaks",
    "google-chrome",
    "mmdc",
    "msedge",
    "npm",
    "npx",
    "opencode",
    "pacman",
    "pdfinfo",
    "pdftoppm",
    "psql",
    "python",
    "python3",
    "pi",
    "scoop",
    "winget",
}
SIGNAL_TITLES = {
    "always": "universal repository workflow",
    "automated_review": "automated review workflow",
    "browser_e2e": "browser E2E tooling",
    "docs_heavy": "documentation-heavy repository",
    "frontend": "frontend application",
    "git": "Git repository",
    "github": "GitHub workflow configuration",
    "knip": "Knip configuration",
    "live_scripts": "migration/backfill/sync scripts",
    "mermaid": "Mermaid diagrams",
    "postgres": "Postgres usage",
    "queue": "Postgres-backed queue code",
    "ralph": "Ralph orchestration",
    "research": "Perplexity research configuration",
    "stale_prs": "stale pull request backlog",
    "tests": "automated tests",
    "typescript": "TypeScript source",
    "web": "web application",
}


def agent_definitions(
    home: Path, env: Mapping[str, str], cwd: Path
) -> list[dict[str, Any]]:
    config_home = Path(env.get("XDG_CONFIG_HOME", home / ".config"))
    app_data = Path(env["APPDATA"]) if env.get("APPDATA") else None
    local_app_data = Path(env["LOCALAPPDATA"]) if env.get("LOCALAPPDATA") else None
    definitions: list[dict[str, Any]] = [
        {
            "id": "codex",
            "name": "Codex",
            "commands": ["codex"],
            "directories": [
                Path(env.get("CODEX_HOME", home / ".codex")),
                Path("/etc/codex"),
            ],
            "environment": ["CODEX_THREAD_ID"],
        },
        {
            "id": "claude-code",
            "name": "Claude Code",
            "commands": ["claude"],
            "directories": [Path(env.get("CLAUDE_CONFIG_DIR", home / ".claude"))],
            "environment": ["CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT"],
        },
        {
            "id": "droid",
            "name": "Factory Droid",
            "commands": ["droid", "factory"],
            "directories": [home / ".factory"],
            "environment": ["FACTORY_SESSION_ID"],
        },
        {
            "id": "cursor",
            "name": "Cursor",
            "commands": ["cursor-agent", "cursor"],
            "directories": [home / ".cursor", Path("/Applications/Cursor.app")],
            "environment": ["CURSOR_AGENT"],
        },
        {
            "id": "opencode",
            "name": "OpenCode",
            "commands": ["opencode"],
            "directories": [config_home / "opencode"],
            "environment": ["OPENCODE_SESSION_ID"],
        },
        {
            "id": "amp",
            "name": "Amp",
            "commands": ["amp"],
            "directories": [config_home / "amp", home / ".amp"],
            "environment": ["AMP_THREAD_ID"],
        },
        {
            "id": "gemini-cli",
            "name": "Gemini CLI",
            "commands": ["gemini"],
            "directories": [home / ".gemini"],
            "environment": ["GEMINI_CLI"],
        },
        {
            "id": "pi",
            "name": "Pi",
            "commands": ["pi"],
            "directories": [home / ".pi" / "agent"],
            "environment": ["PI_AGENT"],
        },
        {
            "id": "github-copilot",
            "name": "GitHub Copilot",
            "commands": ["copilot"],
            "directories": [home / ".copilot"],
            "environment": ["COPILOT_AGENT"],
        },
    ]
    if app_data:
        for definition in definitions:
            if definition["id"] == "cursor":
                definition["directories"].append(app_data / "Cursor")
    if local_app_data:
        for definition in definitions:
            if definition["id"] == "cursor":
                definition["directories"].append(local_app_data / "Programs" / "cursor")
    if (cwd / ".replit").exists():
        definitions.append(
            {
                "id": "replit",
                "name": "Replit",
                "commands": [],
                "directories": [cwd / ".replit"],
                "environment": ["REPL_ID"],
            }
        )
    return definitions


def load_catalog(path: Path = DEFAULT_CATALOG) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != "1.0":
        raise ValueError("catalog schema_version must be 1.0")
    skills = data.get("skills")
    packs = data.get("packs")
    if not isinstance(skills, dict) or not skills:
        raise ValueError("catalog must define skills")
    if not isinstance(packs, dict):
        raise ValueError("catalog must define packs")
    for pack_id, pack in packs.items():
        unknown = sorted(set(pack.get("skills", [])) - set(skills))
        if unknown:
            raise ValueError(
                f"pack {pack_id} references unknown skills: {', '.join(unknown)}"
            )
    return data


def command_paths(path_value: str | None = None) -> dict[str, str | None]:
    return {name: shutil.which(name, path=path_value) for name in sorted(COMMAND_NAMES)}


def linux_distribution() -> str | None:
    release_file = Path("/etc/os-release")
    if not release_file.exists():
        return None
    values: dict[str, str] = {}
    try:
        for line in release_file.read_text(encoding="utf-8").splitlines():
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key] = value.strip().strip('"')
    except OSError:
        return None
    return values.get("PRETTY_NAME") or values.get("ID")


def detect_agents(
    home: Path,
    env: Mapping[str, str],
    commands: Mapping[str, str | None],
    cwd: Path,
) -> list[dict[str, Any]]:
    detected: list[dict[str, Any]] = []
    for definition in agent_definitions(home, env, cwd):
        command_evidence = [
            {"command": command, "path": commands.get(command)}
            for command in definition["commands"]
            if commands.get(command)
        ]
        directory_evidence = [
            str(path) for path in definition["directories"] if path.exists()
        ]
        environment_evidence = [
            key for key in definition["environment"] if env.get(key)
        ]
        if not command_evidence and not directory_evidence and not environment_evidence:
            continue
        active = bool(environment_evidence)
        if active or (command_evidence and directory_evidence):
            confidence = "high"
        elif command_evidence:
            confidence = "medium"
        else:
            confidence = "low"
        if active:
            status = "active"
        elif command_evidence:
            status = "installed"
        else:
            status = "configured"
        evidence: list[str] = []
        evidence.extend(f"command:{item['command']}" for item in command_evidence)
        evidence.extend(f"config:{path}" for path in directory_evidence)
        evidence.extend(f"environment:{key}" for key in environment_evidence)
        detected.append(
            {
                "id": definition["id"],
                "name": definition["name"],
                "status": status,
                "confidence": confidence,
                "evidence": evidence,
            }
        )
    confidence_order = {"high": 0, "medium": 1, "low": 2}
    status_order = {"active": 0, "installed": 1, "configured": 2}
    return sorted(
        detected,
        key=lambda item: (
            status_order[item["status"]],
            confidence_order[item["confidence"]],
            item["name"].lower(),
        ),
    )


def detect_machine(
    home: Path | None = None,
    env: Mapping[str, str] | None = None,
    cwd: Path | None = None,
    path_value: str | None = None,
) -> dict[str, Any]:
    actual_home = home or Path.home()
    actual_env = dict(os.environ if env is None else env)
    actual_cwd = (cwd or Path.cwd()).resolve()
    actual_path = path_value if path_value is not None else actual_env.get("PATH")
    commands = command_paths(actual_path)
    system = platform.system().lower()
    package_managers = [
        name
        for name in ("brew", "apt-get", "dnf", "pacman", "winget", "choco", "scoop")
        if commands.get(name)
    ]
    return {
        "os": system,
        "os_name": platform.system(),
        "distribution": linux_distribution() if system == "linux" else None,
        "architecture": platform.machine(),
        "python": platform.python_version(),
        "home": str(actual_home),
        "commands": commands,
        "package_managers": package_managers,
        "agents": detect_agents(actual_home, actual_env, commands, actual_cwd),
    }


def iter_repository_files(root: Path, limit: int = 5000) -> list[Path]:
    files: list[Path] = []
    for current, directory_names, file_names in os.walk(root):
        directory_names[:] = sorted(
            name
            for name in directory_names
            if name not in IGNORED_DIRECTORIES and not name.startswith(".cache")
        )
        current_path = Path(current)
        for file_name in sorted(file_names):
            path = current_path / file_name
            try:
                relative = path.relative_to(root)
            except ValueError:
                continue
            if any(part in IGNORED_DIRECTORIES for part in relative.parts):
                continue
            files.append(relative)
            if len(files) >= limit:
                return files
    return files


def safe_text(path: Path, max_bytes: int = 1_000_000) -> str:
    try:
        if not path.is_file() or path.stat().st_size > max_bytes:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def fingerprint_repository(root: Path) -> dict[str, Any]:
    root = root.resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"repository path is not a directory: {root}")
    files = iter_repository_files(root)
    file_names = {path.name.lower() for path in files}
    evidence: dict[str, list[str]] = {"always": ["setup baseline"]}

    def add(signal: str, *paths: str | Path) -> None:
        bucket = evidence.setdefault(signal, [])
        for path in paths:
            value = str(path)
            if value not in bucket and len(bucket) < 6:
                bucket.append(value)

    if (root / ".git").exists():
        add("git", ".git")
    if (root / ".github").exists():
        add("github", ".github/")
    if (root / ".ralph").exists():
        add("ralph", ".ralph/")

    readme_paths = [
        path
        for path in files
        if len(path.parts) == 1 and path.name.lower().startswith("readme")
    ]
    if readme_paths:
        add("readme", *readme_paths[:2])

    manifest_paths = [
        path
        for path in files
        if path.name in TEXT_MANIFEST_NAMES
        or re.search(
            r"(?:playwright|cypress|knip|tailwind|next|vite)\.config\.",
            path.name.lower(),
        )
    ][:120]
    manifest_text = "\n".join(safe_text(root / path) for path in manifest_paths).lower()

    cli_paths = [
        path
        for path in files
        if (path.parts and path.parts[0].lower() == "bin")
        or path.stem.lower() in {"cli", "command", "commands"}
        or any(part.lower() in {"cli", "commands"} for part in path.parts[:-1])
    ]
    package_bins: list[Path] = []
    for path in manifest_paths:
        if path.name != "package.json":
            continue
        try:
            manifest = json.loads(safe_text(root / path))
        except json.JSONDecodeError:
            continue
        if isinstance(manifest, dict) and manifest.get("bin"):
            package_bins.append(path)
    if cli_paths or package_bins:
        add("cli", *(cli_paths[:4] or package_bins[:2]))

    typescript_files = [
        path for path in files if path.suffix.lower() in {".ts", ".tsx"}
    ]
    if typescript_files or "tsconfig.json" in file_names:
        add("typescript", *(typescript_files[:3] or ["tsconfig.json"]))

    test_files = []
    for path in files:
        lower_name = path.name.lower()
        test_directory = any(
            part.lower() in {"test", "tests", "__tests__", "spec", "specs"}
            for part in path.parts[:-1]
        )
        test_filename = bool(
            re.search(r"(^test[_-]|[_-]test\.|\.(test|spec)\.)", lower_name)
        )
        if test_directory or test_filename:
            test_files.append(path)
    if test_files:
        add("tests", *test_files[:4])

    web_markers = ("next", "react", "vue", "svelte", "angular", "vite")
    web_paths = [
        path
        for path in manifest_paths
        if any(marker in path.name.lower() for marker in web_markers)
    ]
    if any(f'"{marker}"' in manifest_text for marker in web_markers) or web_paths:
        add("web", *(web_paths[:3] or manifest_paths[:1] or ["package.json"]))

    browser_markers = ("playwright", "cypress")
    browser_paths = [
        path
        for path in files
        if any(marker in path.name.lower() for marker in browser_markers)
    ]
    if any(marker in manifest_text for marker in browser_markers) or browser_paths:
        add("browser_e2e", *(browser_paths[:4] or ["package.json"]))

    frontend_markers = ("tailwind", "src/app", "src/pages", "frontend", "client")
    frontend_paths = [
        path
        for path in files
        if any(marker in str(path).lower() for marker in frontend_markers)
    ]
    if "web" in evidence or frontend_paths:
        add("frontend", *(frontend_paths[:4] or evidence.get("web", [])))

    knip_paths = [path for path in files if "knip" in path.name.lower()]
    if "knip" in manifest_text or knip_paths:
        add("knip", *(knip_paths[:4] or ["package.json"]))

    postgres_markers = ("postgres", "postgresql", "psycopg", "@adonisjs/lucid", '"pg"')
    postgres_paths = [path for path in manifest_paths if "compose" in path.name.lower()]
    if any(marker in manifest_text for marker in postgres_markers):
        add("postgres", *(postgres_paths[:3] or manifest_paths[:2]))

    queue_paths = [
        path
        for path in files
        if re.search(
            r"(^|[/_.-])(queue|queues|worker|workers|job|jobs)([/_.-]|$)",
            str(path).lower(),
        )
    ]
    queue_text = "\n".join(
        safe_text(root / path, 250_000)
        for path in queue_paths[:30]
        if path.suffix.lower() in SOURCE_SUFFIXES
    ).lower()
    if "postgres" in evidence and (
        queue_paths or "skip locked" in queue_text or "queue_jobs" in queue_text
    ):
        add("queue", *queue_paths[:5])

    mermaid_paths = [path for path in files if path.suffix.lower() == ".mmd"]
    if mermaid_paths:
        add("mermaid", *mermaid_paths[:4])

    markdown_paths = [path for path in files if path.suffix.lower() == ".md"]
    docs_paths = [
        path
        for path in markdown_paths
        if path.parts and path.parts[0].lower() in {"docs", "documentation"}
    ]
    if len(docs_paths) >= 3:
        add("docs_heavy", *docs_paths[:4])

    live_script_paths = [
        path
        for path in files
        if path.suffix.lower() in {".py", ".sh", ".js", ".mjs", ".ts"}
        and re.search(
            r"(backfill|migrate|migration|repair|rollout|sync|import|export)",
            path.name.lower(),
        )
    ]
    if live_script_paths:
        add("live_scripts", *live_script_paths[:5])

    automated_review_paths = [
        path
        for path in files
        if ".github/workflows" in str(path).lower()
        and re.search(r"(review|coderabbit|greptile|self-heal)", path.name.lower())
    ]
    if automated_review_paths:
        add("automated_review", *automated_review_paths[:4])

    languages: list[str] = []
    language_markers = [
        ("TypeScript", {".ts", ".tsx"}),
        ("JavaScript", {".js", ".jsx", ".mjs"}),
        ("Python", {".py"}),
        ("Go", {".go"}),
        ("Rust", {".rs"}),
        ("Ruby", {".rb"}),
        ("PHP", {".php"}),
        ("Java/Kotlin", {".java", ".kt"}),
    ]
    suffixes = {path.suffix.lower() for path in files}
    for name, markers in language_markers:
        if suffixes & markers:
            languages.append(name)

    return {
        "path": str(root),
        "file_count_sampled": len(files),
        "scan_limit_reached": len(files) >= 5000,
        "languages": languages,
        "signals": {key: value for key, value in sorted(evidence.items())},
    }


def installed_skills(
    catalog: Mapping[str, Any], repo: Path, home: Path, env: Mapping[str, str]
) -> dict[str, dict[str, list[str]]]:
    config_home = Path(env.get("XDG_CONFIG_HOME", home / ".config"))
    project_roots = [
        repo / ".agents" / "skills",
        repo / ".claude" / "skills",
        repo / ".factory" / "skills",
    ]
    global_roots = [
        home / ".agents" / "skills",
        Path(env.get("CODEX_HOME", home / ".codex")) / "skills",
        Path(env.get("CLAUDE_CONFIG_DIR", home / ".claude")) / "skills",
        home / ".factory" / "skills",
        home / ".cursor" / "skills",
        config_home / "opencode" / "skills",
        config_home / "agents" / "skills",
        home / ".gemini" / "skills",
    ]
    result: dict[str, dict[str, list[str]]] = {"project": {}, "global": {}}
    for scope, roots in (("project", project_roots), ("global", global_roots)):
        for skill_name in catalog["skills"]:
            locations = [
                str(root / skill_name) for root in roots if (root / skill_name).exists()
            ]
            if locations:
                result[scope][skill_name] = sorted(set(locations))
    return result


def evaluate_check(
    check: Mapping[str, Any],
    machine: Mapping[str, Any],
    home: Path,
    env: Mapping[str, str],
) -> tuple[bool, list[str]]:
    check_type = check.get("type")
    commands = machine["commands"]
    if check_type == "command":
        matches = [name for name in check.get("alternatives", []) if commands.get(name)]
        return bool(matches), [f"command:{name}" for name in matches]
    if check_type == "all_commands":
        required = list(check.get("commands", []))
        missing = [name for name in required if not commands.get(name)]
        return not missing, [
            f"command:{name}" for name in required if commands.get(name)
        ]
    if check_type == "env_or_file":
        evidence = [
            f"environment:{key}" for key in check.get("environment", []) if env.get(key)
        ]
        for value in check.get("files", []):
            path = (
                Path(value.replace("~", str(home), 1))
                if value.startswith("~")
                else Path(value)
            )
            if path.exists():
                evidence.append(f"config:{value}")
        return bool(evidence), evidence
    raise ValueError(f"unsupported prerequisite check type: {check_type}")


def evaluate_prerequisites(
    prerequisites: Sequence[Mapping[str, Any]],
    machine: Mapping[str, Any],
    home: Path,
    env: Mapping[str, str],
) -> tuple[str, list[dict[str, Any]]]:
    results: list[dict[str, Any]] = []
    missing_required = False
    missing_provider = False
    missing_conditional = False
    for prerequisite in prerequisites:
        met, evidence = evaluate_check(prerequisite["check"], machine, home, env)
        result = {
            "id": prerequisite["id"],
            "label": prerequisite["label"],
            "kind": prerequisite["kind"],
            "met": met,
            "evidence": evidence,
            "fallback": prerequisite.get("fallback"),
        }
        results.append(result)
        if met:
            continue
        if prerequisite["kind"] == "required":
            missing_required = True
        elif prerequisite["kind"] == "provider":
            missing_provider = True
        else:
            missing_conditional = True
    if missing_required:
        return "needs_setup", results
    if missing_provider:
        return "needs_provider", results
    if missing_conditional:
        return "ready_with_fallbacks", results
    return "ready", results


def recommend_skills(
    catalog: Mapping[str, Any],
    repository: Mapping[str, Any],
    machine: Mapping[str, Any],
    installed: Mapping[str, list[str]],
    selected_packs: Sequence[str],
    selected_skills: Sequence[str],
    home: Path,
    env: Mapping[str, str],
) -> list[dict[str, Any]]:
    signal_names = set(repository["signals"])
    pack_skills: set[str] = set()
    explicit_skills = set(selected_skills)
    skill_pack_reasons: dict[str, list[str]] = {}
    for pack_id in selected_packs:
        pack = catalog["packs"][pack_id]
        for skill_name in pack["skills"]:
            pack_skills.add(skill_name)
            skill_pack_reasons.setdefault(skill_name, []).append(pack["title"])

    recommendations: list[dict[str, Any]] = []
    for skill_name, definition in catalog["skills"].items():
        matching_signals = sorted(set(definition.get("signals", [])) & signal_names)
        selected_by_pack = skill_name in pack_skills
        selected_explicitly = skill_name in explicit_skills
        if not matching_signals and not selected_by_pack and not selected_explicitly:
            continue
        status, prerequisites = evaluate_prerequisites(
            definition.get("prerequisites", []), machine, home, env
        )
        reasons: list[str] = []
        for signal in matching_signals:
            title = SIGNAL_TITLES.get(signal, signal.replace("_", " "))
            signal_evidence = repository["signals"].get(signal, [])
            if signal == "always":
                reasons.append(title)
            elif signal_evidence:
                reasons.append(f"{title}: {', '.join(signal_evidence[:2])}")
            else:
                reasons.append(title)
        for pack_title in skill_pack_reasons.get(skill_name, []):
            reasons.append(f"selected pack: {pack_title}")
        if selected_explicitly:
            reasons.append("selected explicitly")
        recommendations.append(
            {
                "name": skill_name,
                "summary": definition["summary"],
                "priority": definition["priority"],
                "status": status,
                "installed": skill_name in installed,
                "installed_locations": installed.get(skill_name, []),
                "reasons": reasons,
                "prerequisites": prerequisites,
            }
        )
    return sorted(recommendations, key=lambda item: (item["priority"], item["name"]))


def build_install_argv(
    source: str,
    skills: Sequence[str],
    agents: Sequence[str],
    global_scope: bool,
) -> list[str]:
    argv = ["npx", "skills@latest", "add", source, "--skill", *skills, "--copy"]
    if agents:
        argv.extend(["--agent", *agents])
    if global_scope:
        argv.append("--global")
    if agents:
        argv.append("-y")
    return argv


def shell_command(argv: Sequence[str], os_name: str) -> str:
    if os_name == "windows":
        return subprocess.list2cmdline(list(argv))
    return shlex.join(argv)


def build_report(
    repo: Path,
    catalog: Mapping[str, Any],
    selected_packs: Sequence[str],
    selected_skills: Sequence[str],
    selected_agents: Sequence[str],
    global_scope: bool,
    home: Path | None = None,
    env: Mapping[str, str] | None = None,
    path_value: str | None = None,
) -> dict[str, Any]:
    actual_home = home or Path.home()
    actual_env = dict(os.environ if env is None else env)
    repository = fingerprint_repository(repo)
    machine = detect_machine(actual_home, actual_env, repo, path_value)
    installed = installed_skills(catalog, repo.resolve(), actual_home, actual_env)
    scope_name = "global" if global_scope else "project"
    scope_installed = installed[scope_name]
    recommendations = recommend_skills(
        catalog,
        repository,
        machine,
        scope_installed,
        selected_packs,
        selected_skills,
        actual_home,
        actual_env,
    )
    recommendation_names = [item["name"] for item in recommendations]
    planned_names = list(selected_skills) if selected_skills else recommendation_names
    scope_installed_names = set(scope_installed)
    to_install = [name for name in planned_names if name not in scope_installed_names]
    argv = (
        build_install_argv(catalog["source"], to_install, selected_agents, global_scope)
        if to_install
        else []
    )
    counts: dict[str, int] = {}
    for recommendation in recommendations:
        counts[recommendation["status"]] = counts.get(recommendation["status"], 0) + 1
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "global" if global_scope else "project",
        "selected_packs": list(selected_packs),
        "selected_skills": list(selected_skills),
        "selected_agents": list(selected_agents),
        "machine": machine,
        "repository": repository,
        "installed_skills": installed,
        "recommendations": recommendations,
        "status_counts": counts,
        "install_plan": {
            "skills": to_install,
            "available": bool(machine["commands"].get("npx")),
            "argv": argv,
            "command": shell_command(argv, machine["os"]) if argv else "",
        },
    }


def render_text(report: Mapping[str, Any], catalog: Mapping[str, Any]) -> str:
    machine = report["machine"]
    repository = report["repository"]
    lines = [
        "AGENT SKILLS DOCTOR",
        "",
        f"Machine: {machine['os_name']} · {machine['architecture']} · Python {machine['python']}",
    ]
    if machine.get("distribution"):
        lines.append(f"Distribution: {machine['distribution']}")
    if machine["package_managers"]:
        lines.append(f"Package managers: {', '.join(machine['package_managers'])}")
    lines.append("")
    lines.append("Detected coding agents")
    if machine["agents"]:
        for agent in machine["agents"]:
            lines.append(
                f"  [{agent['confidence'].upper()}] {agent['name']} — {agent['status']} "
                f"({', '.join(agent['evidence'])})"
            )
    else:
        lines.append(
            "  None detected confidently; the Skills CLI can still prompt for targets."
        )

    lines.extend(
        [
            "",
            "Repository",
            f"  Path: {repository['path']}",
            f"  Languages: {', '.join(repository['languages']) or 'not confidently detected'}",
            f"  Files sampled: {repository['file_count_sampled']}"
            + (" (scan limit reached)" if repository["scan_limit_reached"] else ""),
            "  Signals:",
        ]
    )
    for signal, evidence in repository["signals"].items():
        if signal == "always":
            continue
        lines.append(
            f"    - {SIGNAL_TITLES.get(signal, signal)}: {', '.join(evidence)}"
        )

    if report["selected_packs"]:
        lines.extend(["", "Selected packs"])
        for pack_id in report["selected_packs"]:
            pack = catalog["packs"][pack_id]
            lines.append(f"  - {pack['title']}: {pack['description']}")

    lines.extend(["", "Suggested flight plan"])
    status_labels = {
        "ready": "READY",
        "ready_with_fallbacks": "FALLBACK",
        "needs_provider": "PROVIDER",
        "needs_setup": "SETUP",
    }
    for index, recommendation in enumerate(report["recommendations"], 1):
        installed_label = " · installed" if recommendation["installed"] else ""
        lines.append(
            f"  {index}. [{status_labels[recommendation['status']]}] "
            f"{recommendation['name']}{installed_label}"
        )
        lines.append(f"     {recommendation['summary']}")
        lines.append(f"     Why: {'; '.join(recommendation['reasons'])}")
        missing = [item for item in recommendation["prerequisites"] if not item["met"]]
        for prerequisite in missing:
            lines.append(
                f"     Missing {prerequisite['kind']}: {prerequisite['label']}"
                + (
                    f" — {prerequisite['fallback']}"
                    if prerequisite.get("fallback")
                    else ""
                )
            )

    lines.extend(["", "Readiness summary"])
    for status in ("ready", "ready_with_fallbacks", "needs_provider", "needs_setup"):
        lines.append(
            f"  {status.replace('_', ' ').title()}: {report['status_counts'].get(status, 0)}"
        )

    lines.extend(["", "Project vendoring plan"])
    if report["install_plan"]["skills"]:
        lines.append(f"  Scope: {report['scope']}")
        lines.append(f"  Skills: {', '.join(report['install_plan']['skills'])}")
        lines.append(f"  Command: {report['install_plan']['command']}")
        if not report["install_plan"]["available"]:
            lines.append(
                "  npx is not available; install Node.js or vendor the folders manually."
            )
    else:
        lines.append(
            "  Every recommended skill is already installed in a discovered location."
        )

    lines.extend(
        [
            "",
            "Next",
            "  1. Review the recommendation evidence and prerequisite fallbacks.",
            "  2. Confirm the exact skills, project/global scope, and target agents.",
            "  3. Run the printed command or rerun with --install --yes after approval.",
            "  4. Start with a read-only $agent-readiness-scoring audit.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo", type=Path, default=Path.cwd(), help="Repository to inspect"
    )
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--output", type=Path, help="Write the report to this file")
    parser.add_argument(
        "--pack", action="append", default=[], help="Outcome pack to include"
    )
    parser.add_argument(
        "--skill", action="append", default=[], help="Exact skill to plan or install"
    )
    parser.add_argument(
        "--agent", action="append", default=[], help="Skills CLI agent target"
    )
    parser.add_argument(
        "--global-scope", action="store_true", help="Plan a global installation"
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Execute the generated Skills CLI command",
    )
    parser.add_argument(
        "--yes", action="store_true", help="Confirm an explicit --install operation"
    )
    parser.add_argument(
        "--list-packs", action="store_true", help="List available outcome packs"
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_arguments(argv)
    try:
        catalog = load_catalog(arguments.catalog)
        unknown_packs = sorted(set(arguments.pack) - set(catalog["packs"]))
        if unknown_packs:
            raise ValueError(f"unknown pack(s): {', '.join(unknown_packs)}")
        unknown_skills = sorted(set(arguments.skill) - set(catalog["skills"]))
        if unknown_skills:
            raise ValueError(f"unknown skill(s): {', '.join(unknown_skills)}")
        if arguments.list_packs:
            for pack_id, pack in catalog["packs"].items():
                print(f"{pack_id}\t{pack['title']}\t{pack['description']}")
            return 0
        if arguments.install and not arguments.yes:
            raise ValueError(
                "--install requires --yes after the user approves the exact plan"
            )
        if arguments.install and not arguments.agent:
            raise ValueError("--install requires at least one explicit --agent target")
        report = build_report(
            arguments.repo,
            catalog,
            arguments.pack,
            arguments.skill,
            arguments.agent,
            arguments.global_scope,
        )
        rendered = (
            json.dumps(report, indent=2) + "\n"
            if arguments.format == "json"
            else render_text(report, catalog)
        )
        if arguments.output:
            arguments.output.parent.mkdir(parents=True, exist_ok=True)
            arguments.output.write_text(rendered, encoding="utf-8")
            print(f"Wrote {arguments.output.resolve()}")
        else:
            print(rendered, end="")
        if arguments.install:
            if not report["install_plan"]["available"]:
                raise ValueError("cannot install because npx is not available")
            if not report["install_plan"]["skills"]:
                print("No installation needed.")
                return 0
            completed = subprocess.run(
                report["install_plan"]["argv"],
                cwd=arguments.repo.resolve(),
                check=False,
            )
            return completed.returncode
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
