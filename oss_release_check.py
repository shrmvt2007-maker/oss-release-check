#!/usr/bin/env python3
"""Check whether a local repository has common open-source release basics."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    check: str
    status: str
    message: str
    paths: tuple[str, ...] = ()


def first_existing(root: Path, candidates: tuple[str, ...]) -> Path | None:
    for candidate in candidates:
        path = root / candidate
        if path.is_file():
            return path
    return None


def has_nontrivial_text(path: Path) -> bool:
    try:
        return len(path.read_text(encoding="utf-8", errors="replace").strip()) >= 40
    except OSError:
        return False


def inspect(root: Path) -> list[Finding]:
    checks: list[Finding] = []
    groups = [
        ("README", ("README.md", "README.rst", "README.txt", "README"), "Explain what the project does and how to use it."),
        ("LICENSE", ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"), "Add a license so users know how they may use and share the code."),
        ("CONTRIBUTING", ("CONTRIBUTING.md", "CONTRIBUTING.rst", ".github/CONTRIBUTING.md"), "Describe how to propose changes and report bugs."),
        ("CODE_OF_CONDUCT", ("CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md"), "Set expectations for respectful participation."),
        ("SECURITY", ("SECURITY.md", ".github/SECURITY.md"), "Explain how to report security issues privately."),
        ("CHANGELOG", ("CHANGELOG.md", "CHANGES.md", "HISTORY.md"), "Keep a human-readable record of notable changes."),
    ]
    for name, paths, advice in groups:
        found = first_existing(root, paths)
        status = "present" if found and has_nontrivial_text(found) else "missing"
        checks.append(Finding(name, status, "Found." if status == "present" else advice, (str(found.relative_to(root)) ,) if found else ()))

    workflow_dir = root / ".github" / "workflows"
    workflows = sorted(p for p in workflow_dir.glob("*") if p.is_file()) if workflow_dir.is_dir() else []
    checks.append(Finding(
        "CI_WORKFLOW",
        "present" if workflows else "missing",
        "Found a workflow file." if workflows else "Add continuous integration that runs the checks contributors rely on.",
        tuple(str(p.relative_to(root)) for p in workflows[:5]),
    ))

    issue_dir = root / ".github" / "ISSUE_TEMPLATE"
    templates = sorted(p for p in issue_dir.glob("*") if p.is_file()) if issue_dir.is_dir() else []
    has_config = (root / ".github" / "ISSUE_TEMPLATE.md").is_file() or (root / ".github" / "ISSUE_TEMPLATE").is_file()
    checks.append(Finding(
        "ISSUE_GUIDANCE",
        "present" if templates or has_config else "optional",
        "Issue templates or guidance are available." if templates or has_config else "Optional: add issue templates if structured reports would help maintainers.",
        tuple(str(p.relative_to(root)) for p in templates[:5]),
    ))

    pyproject = root / "pyproject.toml"
    package_json = root / "package.json"
    cargo = root / "Cargo.toml"
    metadata = next((p for p in (pyproject, package_json, cargo) if p.is_file()), None)
    if metadata:
        text = metadata.read_text(encoding="utf-8", errors="replace")
        license_hint = bool(re.search(r"(?im)^\s*(license|license-file)\s*[:=]", text))
        checks.append(Finding(
            "PACKAGE_LICENSE_METADATA",
            "present" if license_hint else "review",
            "A license field appears in package metadata." if license_hint else "Review package metadata and add its ecosystem's license field if applicable.",
            (str(metadata.relative_to(root)),),
        ))
    else:
        checks.append(Finding("PACKAGE_LICENSE_METADATA", "optional", "No common package manifest found; this check may not apply."))

    return checks


def render_markdown(root: Path, findings: list[Finding]) -> str:
    passed = sum(f.status == "present" for f in findings)
    lines = [f"# Open-source release checklist: `{root.name}`", "", f"{passed} of {len(findings)} checks marked present.", "", "This report checks for files and simple metadata only. It does not assess code quality, legal suitability, security, project impact, or program eligibility.", "", "| Check | Status | Notes |", "|---|---|---|"]
    for f in findings:
        paths = f" ({', '.join(f.paths)})" if f.paths else ""
        lines.append(f"| {f.check} | {f.status} | {f.message}{paths} |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".", help="repository directory (default: current directory)")
    parser.add_argument("--format", choices=("text", "json", "markdown"), default="text", help="report format")
    args = parser.parse_args(argv)
    root = Path(args.path).expanduser().resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")
    findings = inspect(root)
    if args.format == "json":
        print(json.dumps({"repository": str(root), "findings": [asdict(f) for f in findings]}, indent=2))
    elif args.format == "markdown":
        print(render_markdown(root, findings), end="")
    else:
        for f in findings:
            marker = {"present": "[OK]", "missing": "[TODO]", "review": "[REVIEW]", "optional": "[INFO]"}[f.status]
            suffix = f" — {', '.join(f.paths)}" if f.paths else ""
            print(f"{marker} {f.check}: {f.message}{suffix}")
        print("\nThis checks repository signals only. It is not a quality, legal, security, impact, or eligibility assessment.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
