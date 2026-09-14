#!/usr/bin/env python3
"""Dependency-free static consistency check for Agentic Harness Foundry.

Run before starting the self-build and after documentation/task-graph changes.
This script is intentionally read-only.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md",
    "AGENTS.md",
    "TASKS.md",
    ".gitignore",
    "docs/architecture.md",
    "docs/build-readiness.md",
    "docs/early-wins.md",
    "docs/evidence-policy.md",
    "docs/roadmap.md",
    "docs/spec-lite.md",
    "docs/testing-strategy.md",
    "docs/specs/local-model-admission.md",
    "docs/specs/m2-context-memory-security.md",
    "docs/specs/m3-pi-worker-rpc.md",
    "prompts/hermes-bootstrap.md",
    "scripts/check_repo.py",
    "scripts/preflight.sh",
]

FORBIDDEN_TRACKED_PREFIXES = (
    "evidence/",
    "evals/private/",
    ".local/",
    "local/",
    "tmp/",
    ".cache/",
)
FORBIDDEN_TRACKED_SUFFIXES = (
    ".gguf",
    ".safetensors",
    ".bin",
    ".pem",
    ".key",
    ".p12",
    ".pfx",
)

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
TASK_RE = re.compile(r"\*\*T(\d{3})\b")
UNCHECKED_RE = re.compile(r"^- \[ \] \*\*T(\d{3})\b", re.MULTILINE)
DB_RE = re.compile(r"\.(?:db|sqlite|sqlite3)(?:-.+)?$")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def check_required(errors: list[str]) -> None:
    for relative in REQUIRED:
        if not (ROOT / relative).exists():
            fail(errors, f"missing required path: {relative}")


def normalize_markdown_target(raw: str) -> str | None:
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    # Drop an optional Markdown title after whitespace. None of the Foundry
    # source-of-truth links need spaces in their paths.
    target = target.split(maxsplit=1)[0]
    if not target or target.startswith("#"):
        return None
    parsed = urlparse(target)
    if parsed.scheme or parsed.netloc:
        return None
    path = unquote(parsed.path)
    return path or None


def check_markdown_links(errors: list[str]) -> None:
    for md in sorted(ROOT.rglob("*.md")):
        if ".git" in md.parts:
            continue
        text = md.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            path = normalize_markdown_target(match.group(1))
            if path is None or path.startswith("/"):
                continue
            resolved = (md.parent / path).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                fail(errors, f"link escapes repo: {md.relative_to(ROOT)} -> {path}")
                continue
            if not resolved.exists():
                fail(errors, f"broken local link: {md.relative_to(ROOT)} -> {path}")


def check_tasks(errors: list[str]) -> None:
    task_file = ROOT / "TASKS.md"
    if not task_file.exists():
        return
    text = task_file.read_text(encoding="utf-8")
    task_ids = TASK_RE.findall(text)
    if not task_ids:
        fail(errors, "TASKS.md contains no task IDs")
        return
    duplicates = sorted({task for task in task_ids if task_ids.count(task) > 1})
    if duplicates:
        fail(errors, f"duplicate task IDs: {', '.join('T' + x for x in duplicates)}")
    unchecked = UNCHECKED_RE.findall(text)
    if not unchecked:
        fail(errors, "TASKS.md has no unchecked task; confirm mission is actually complete")
    elif unchecked[0] != "001":
        print(f"INFO: first unchecked task is T{unchecked[0]} (T001 is no longer first).")


def git_tracked_files() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "-z"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    return [p.decode("utf-8", errors="replace") for p in result.stdout.split(b"\0") if p]


def check_sensitive_tracking(errors: list[str]) -> None:
    tracked = git_tracked_files()
    if not tracked:
        print("INFO: git tracked-file check unavailable or repository has no tracked files.")
        return
    for path in tracked:
        lower = path.lower()
        if path.startswith(FORBIDDEN_TRACKED_PREFIXES):
            fail(errors, f"sensitive/local path is tracked: {path}")
        if lower == ".env" or (lower.startswith(".env.") and lower != ".env.example"):
            fail(errors, f"environment file is tracked: {path}")
        if lower.endswith(FORBIDDEN_TRACKED_SUFFIXES) or DB_RE.search(lower):
            fail(errors, f"sensitive/model artifact is tracked: {path}")


def check_gitignore(errors: list[str]) -> None:
    path = ROOT / ".gitignore"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    for required in ("evidence/", "evals/private/", "*.gguf", "*.db"):
        if required not in text:
            fail(errors, f".gitignore missing required protection: {required}")


def main() -> int:
    errors: list[str] = []
    check_required(errors)
    check_markdown_links(errors)
    check_tasks(errors)
    check_gitignore(errors)
    check_sensitive_tracking(errors)

    if errors:
        print("Foundry repo check: FAIL")
        for item in errors:
            print(f"- {item}")
        return 1

    print("Foundry repo check: PASS")
    print("- required source-of-truth files present")
    print("- local Markdown links resolve")
    print("- task IDs are unique")
    print("- sensitive evidence/model paths are not tracked")
    print("- baseline gitignore protections are present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
