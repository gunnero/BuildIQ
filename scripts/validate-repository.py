#!/usr/bin/env python3
"""Validate public repository documentation and GitHub configuration."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def markdown_links() -> list[str]:
    failures: list[str] = []
    files = [ROOT / name for name in ("README.md", "SECURITY.md", "CONTRIBUTING.md", "CHANGELOG.md")]
    files.extend((ROOT / "docs").glob("*.md"))
    for path in files:
        text = path.read_text(encoding="utf-8")
        for raw_target in re.findall(r"!?\[[^]]*\]\(([^)]+)\)", text):
            target = raw_target.strip().split()[0].strip("<>")
            if "://" in target or target.startswith(("#", "mailto:")):
                continue
            local_target = target.split("#", maxsplit=1)[0]
            if local_target and not (path.parent / local_target).exists():
                failures.append(f"{path.relative_to(ROOT)}: missing {target}")
    return failures


def github_yaml() -> list[str]:
    failures: list[str] = []
    for path in (ROOT / ".github").rglob("*.yml"):
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as error:
            failures.append(f"{path.relative_to(ROOT)}: {error}")
    return failures


def architecture_svg() -> list[str]:
    source = (ROOT / "docs/architecture.mmd").read_text(encoding="utf-8")
    exported = (ROOT / "docs/architecture.svg").read_text(encoding="utf-8")
    labels = re.findall(r"(?:\[|\[\(|\|)([A-Za-z][A-Za-z ]+)(?:\]|\)\]|\|)", source)
    return [f"docs/architecture.svg: missing label {label!r}" for label in labels if label not in exported]


def sensitive_topology() -> list[str]:
    patterns = {
        "server name": re.compile(r"\bweb0[0-9]\b", re.IGNORECASE),
        "private domain": re.compile(r"buildiq\.(?:kalveri\.com|razbudise\.mk)", re.IGNORECASE),
        "known IP range": re.compile(r"\b188\.245\.\d{1,3}\.\d{1,3}\b"),
        "SSH command": re.compile(r"\bssh\s+", re.IGNORECASE),
        "private home path": re.compile(r"/home/[A-Za-z0-9._-]+"),
    }
    exclusions = {
        Path("docs/github-professionalization-buildiq.md"),
        Path("docs/dependency-remediation-plan.md"),
        Path("docs/licensing-decision.md"),
        Path("docs/036-dependency-remediation-review.md"),
        Path("scripts/validate-repository.py"),
    }
    failures: list[str] = []
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if not path.is_file() or relative in exclusions or any(part in {".git", ".venv", "node_modules", "tmp"} for part in relative.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for name, pattern in patterns.items():
            if pattern.search(text):
                failures.append(f"{relative}: contains {name}")
    return failures


def main() -> int:
    failures = markdown_links() + github_yaml() + architecture_svg() + sensitive_topology()
    if failures:
        print("Repository validation failed:")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print("Repository validation passed: Markdown, GitHub YAML, architecture SVG, and topology.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
