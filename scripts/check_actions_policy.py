#!/usr/bin/env python3
"""Offline guard for the base GitHub Actions cost-control policy."""

from __future__ import annotations

import re
from pathlib import Path

ALLOWED_WORKFLOWS = {"ci.yml"}
REQUIRED_WORKFLOWS = {"ci.yml"}
MAX_TIMEOUT_MINUTES = 15

DOC_REQUIREMENTS = {
    "AGENTS.md": (
        "CI is a review/release gate, not an iterative debugger.",
        "batch",
        "NOT_RUN — no agent-controlled executable workspace",
        "pull_request_target",
    ),
    "docs/GITHUB_ACTIONS_POLICY.md": (
        "types: [ready_for_review]",
        "synchronize",
        "workflow_dispatch",
        "cancel-in-progress: true",
        "one batch push",
        "persist-credentials: false",
    ),
}


def read_text(path: Path) -> str:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"missing or unsafe file: {path}")
    return path.read_text(encoding="utf-8")


def top_level_block(text: str, name: str) -> str:
    match = re.search(rf"(?m)^{re.escape(name)}:\s*$", text)
    if not match:
        return ""
    start = match.end()
    next_key = re.search(r"(?m)^[A-Za-z0-9_-]+:\s*(?:#.*)?$", text[start:])
    end = start + next_key.start() if next_key else len(text)
    return text[start:end]


def nested_block(text: str, name: str) -> str:
    match = re.search(rf"(?m)^  {re.escape(name)}:\s*$", text)
    if not match:
        return ""
    start = match.end()
    next_key = re.search(r"(?m)^  [A-Za-z0-9_-]+:\s*(?:#.*)?$", text[start:])
    end = start + next_key.start() if next_key else len(text)
    return text[start:end]


def check_ci(text: str) -> list[str]:
    errors: list[str] = []

    trigger = top_level_block(text, "on")
    if not trigger:
        return ["ci.yml: explicit top-level on block is required"]

    pr = nested_block(trigger, "pull_request")
    if not pr:
        errors.append("ci.yml: pull_request block is required")
    else:
        if not re.search(r"(?m)^    types:\s*\[\s*ready_for_review\s*\]\s*$", pr):
            errors.append("ci.yml: pull_request must use only types: [ready_for_review]")
        if re.search(r"\bsynchronize\b", pr):
            errors.append("ci.yml: synchronize trigger is forbidden")

    push = nested_block(trigger, "push")
    if not push or not re.search(r"(?m)^      - main\s*$", push):
        errors.append("ci.yml: push-to-main verification is required")

    if not re.search(r"(?m)^  workflow_dispatch:\s*$", trigger):
        errors.append("ci.yml: workflow_dispatch is required")

    if "pull_request_target:" in text:
        errors.append("ci.yml: pull_request_target is forbidden in the base policy")

    permissions = top_level_block(text, "permissions")
    if not permissions or not re.search(r"(?m)^  contents:\s*read\s*$", permissions):
        errors.append("ci.yml: default contents permission must be read-only")
    if "write-all" in text:
        errors.append("ci.yml: write-all permission is forbidden")

    concurrency = top_level_block(text, "concurrency")
    if not concurrency:
        errors.append("ci.yml: concurrency block is required")
    else:
        if not re.search(r"(?m)^  group:\s*\S+", concurrency):
            errors.append("ci.yml: concurrency group is required")
        if not re.search(r"(?m)^  cancel-in-progress:\s*true\s*$", concurrency):
            errors.append("ci.yml: cancel-in-progress must be true")

    timeouts = [
        int(value)
        for value in re.findall(r"(?m)^    timeout-minutes:\s*(\d+)\s*$", text)
    ]
    if not timeouts:
        errors.append("ci.yml: every base job must define timeout-minutes")
    elif any(value < 1 or value > MAX_TIMEOUT_MINUTES for value in timeouts):
        errors.append(
            f"ci.yml: timeout-minutes must be between 1 and {MAX_TIMEOUT_MINUTES}"
        )

    if "persist-credentials: false" not in text:
        errors.append("ci.yml: checkout must disable persisted credentials")

    if "python3 scripts/check_actions_policy.py" not in text:
        errors.append("ci.yml: policy self-check step is required")

    return errors


def check(root: Path) -> list[str]:
    errors: list[str] = []
    workflow_dir = root / ".github" / "workflows"

    if not workflow_dir.is_dir():
        errors.append("workflow directory is missing")
        workflow_files: dict[str, Path] = {}
    else:
        workflow_files = {
            path.name: path
            for path in workflow_dir.iterdir()
            if path.is_file() and path.suffix in {".yml", ".yaml"}
        }

    unknown = sorted(set(workflow_files) - ALLOWED_WORKFLOWS)
    if unknown:
        errors.append(f"unregistered workflow files: {unknown}")

    missing = sorted(REQUIRED_WORKFLOWS - set(workflow_files))
    for name in missing:
        errors.append(f"required workflow is missing: {name}")

    ci_path = workflow_files.get("ci.yml")
    if ci_path:
        try:
            errors.extend(check_ci(read_text(ci_path)))
        except (OSError, ValueError) as exc:
            errors.append(str(exc))

    for relative, tokens in DOC_REQUIREMENTS.items():
        path = root / relative
        try:
            text = read_text(path)
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
            continue
        missing_tokens = [token for token in tokens if token not in text]
        if missing_tokens:
            errors.append(f"{relative}: policy tokens missing: {missing_tokens}")

    return errors


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    errors = check(root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        raise SystemExit(1)
    print(
        "PASS: registered workflows preserve final-review triggers, least privilege, "
        "bounded concurrency/timeouts, and the base Actions cost-control policy"
    )


if __name__ == "__main__":
    main()
