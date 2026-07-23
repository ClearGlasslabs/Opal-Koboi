#!/usr/bin/env python3
"""ClearGlass Artemis CI supply-chain policy gate.

Dependency-free, fail-closed scanner for GitHub Actions workflow files.
It identifies high-risk trigger/permission/check-out combinations, mutable
third-party action references, expression injection into shell blocks, and
credential persistence that expands an attacker's blast radius.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

ACTION_RE = re.compile(r"^\s*uses:\s*([^\s#]+)", re.MULTILINE)
FULL_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
EVENT_LINE_RE = re.compile(
    r"^\s{0,4}(pull_request_target|pull_request|issue_comment|issues|"
    r"discussion|discussion_comment|workflow_run)\s*:",
    re.MULTILINE,
)
RUN_BLOCK_RE = re.compile(r"^\s*run:\s*[|>]\s*\n(?P<body>(?:^[ \t]+.*\n?)*)", re.MULTILINE)
DANGEROUS_EXPR_RE = re.compile(
    r"\$\{\{\s*github\.event\.(issue\.title|issue\.body|comment\.body|"
    r"pull_request\.title|pull_request\.body|review\.body|"
    r"head_commit\.message|commits)\b"
)
WRITE_PERMISSION_RE = re.compile(
    r"^\s*(contents|actions|packages|deployments|pages|pull-requests|issues|"
    r"checks|statuses|repository-projects):\s*write\s*$",
    re.MULTILINE,
)


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    path: str
    line: int
    message: str
    remediation: str


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def contains_untrusted_checkout(text: str) -> bool:
    patterns = (
        "github.event.pull_request.head.sha",
        "github.event.pull_request.head.ref",
        "github.event.workflow_run.head_sha",
        "refs/pull/",
    )
    return "actions/checkout@" in text and any(pattern in text for pattern in patterns)


def scan_workflow(path: Path, policy: dict) -> list[Finding]:
    text = path.read_text(encoding="utf-8")
    findings: list[Finding] = []
    relative = path.as_posix()
    events = set(EVENT_LINE_RE.findall(text))
    untrusted_events = events.intersection(policy["untrusted_events"])

    if "pull_request_target" in events:
        offset = text.find("pull_request_target")
        severity = "critical" if "actions/checkout@" in text else "high"
        findings.append(
            Finding(
                "CG-ACT-001",
                severity,
                relative,
                line_number(text, offset),
                "`pull_request_target` executes in the privileged base-repository context.",
                "Use `pull_request` for validation or split privileged work into a separately reviewed `workflow_run` job that never executes PR-controlled code or artifacts.",
            )
        )

    if untrusted_events and contains_untrusted_checkout(text):
        offset = min(
            (text.find(p) for p in (
                "github.event.pull_request.head.sha",
                "github.event.pull_request.head.ref",
                "github.event.workflow_run.head_sha",
                "refs/pull/",
            ) if p in text),
            default=0,
        )
        findings.append(
            Finding(
                "CG-ACT-002",
                "critical",
                relative,
                line_number(text, offset),
                "A privileged or cross-workflow path checks out attacker-controlled code.",
                "Do not check out or execute untrusted refs in privileged workflows. Pass narrowly scoped, verified data instead.",
            )
        )

    if untrusted_events:
        for match in WRITE_PERMISSION_RE.finditer(text):
            permission = match.group(1)
            findings.append(
                Finding(
                    "CG-ACT-003",
                    "high",
                    relative,
                    line_number(text, match.start()),
                    f"Untrusted event has `{permission}: write` permission.",
                    "Move write operations to a trusted workflow, use an environment approval gate, and grant permissions only at the job that requires them.",
                )
            )

    if untrusted_events and re.search(r"^\s*id-token:\s*write\s*$", text, re.MULTILINE):
        offset = re.search(r"^\s*id-token:\s*write\s*$", text, re.MULTILINE)
        assert offset is not None
        findings.append(
            Finding(
                "CG-ACT-004",
                "critical",
                relative,
                line_number(text, offset.start()),
                "OIDC token minting is enabled for a workflow reachable from an untrusted event.",
                "Issue OIDC tokens only in protected deployment jobs triggered from trusted refs and bound to a protected GitHub Environment.",
            )
        )

    for match in ACTION_RE.finditer(text):
        reference = match.group(1)
        if reference.startswith("./") or reference.startswith("docker://"):
            continue
        if "@" not in reference:
            findings.append(
                Finding(
                    "CG-ACT-005",
                    "critical",
                    relative,
                    line_number(text, match.start()),
                    f"Action reference `{reference}` has no immutable revision.",
                    "Pin every external action to a verified full-length commit SHA.",
                )
            )
            continue
        action, ref = reference.rsplit("@", 1)
        if not FULL_SHA_RE.fullmatch(ref) and reference not in policy.get("allowed_mutable_refs", []):
            findings.append(
                Finding(
                    "CG-ACT-005",
                    "high",
                    relative,
                    line_number(text, match.start()),
                    f"Action `{action}` uses mutable ref `{ref}`.",
                    "Resolve the release tag to its verified 40-character commit SHA and retain the release tag in a comment.",
                )
            )

    for match in RUN_BLOCK_RE.finditer(text):
        body = match.group("body")
        dangerous = DANGEROUS_EXPR_RE.search(body)
        if dangerous:
            findings.append(
                Finding(
                    "CG-ACT-006",
                    "high",
                    relative,
                    line_number(text, match.start()),
                    f"Untrusted expression `{dangerous.group(0)}` is interpolated directly into a shell script.",
                    "Assign event data to an environment variable and treat it strictly as data; never splice it into executable shell source.",
                )
            )

    lines = text.splitlines(keepends=True)
    line_offsets: list[int] = []
    offset = 0
    for line in lines:
        line_offsets.append(offset)
        offset += len(line)

    for index, line in enumerate(lines):
        if not re.match(r"^\s*(?:-\s+)?uses:\s*actions/checkout@", line):
            continue

        step_start = index
        while step_start >= 0 and not re.match(r"^(?P<indent>\s*)-\s+", lines[step_start]):
            step_start -= 1
        if step_start < 0:
            continue

        indent_match = re.match(r"^(?P<indent>\s*)-\s+", lines[step_start])
        assert indent_match is not None
        step_indent = len(indent_match.group("indent"))
        step_end = step_start + 1
        while step_end < len(lines):
            candidate = re.match(r"^(?P<indent>\s*)-\s+", lines[step_end])
            if candidate and len(candidate.group("indent")) == step_indent:
                break
            step_end += 1

        block = "".join(lines[step_start:step_end])
        if "persist-credentials: false" not in block:
            findings.append(
                Finding(
                    "CG-ACT-007",
                    "medium",
                    relative,
                    line_number(text, line_offsets[step_start]),
                    "`actions/checkout` leaves the workflow token available to later steps.",
                    "Set `persist-credentials: false` unless a reviewed step must push with that token.",
                )
            )

    if untrusted_events and re.search(r"runs-on:\s*(?:\[[^\]]*self-hosted|self-hosted)", text):
        offset = text.find("self-hosted")
        findings.append(
            Finding(
                "CG-ACT-008",
                "critical",
                relative,
                line_number(text, offset),
                "An untrusted event can reach a self-hosted runner.",
                "Do not expose persistent self-hosted runners to fork or public contribution events. Use isolated ephemeral runners with no ambient credentials.",
            )
        )

    if "workflow_run" in events and re.search(r"actions/download-artifact@", text):
        offset = text.find("actions/download-artifact@")
        findings.append(
            Finding(
                "CG-ACT-009",
                "high",
                relative,
                line_number(text, offset),
                "A privileged `workflow_run` consumes artifacts without an explicit provenance check.",
                "Bind the artifact to the expected repository, workflow, run ID, head SHA, and triggering actor before extraction or execution.",
            )
        )

    if re.search(r"^\s*permissions:\s*write-all\s*$", text, re.MULTILINE):
        offset = text.find("write-all")
        findings.append(
            Finding(
                "CG-ACT-010",
                "critical",
                relative,
                line_number(text, offset),
                "`permissions: write-all` grants unnecessary repository-wide authority.",
                "Declare `permissions: {}` globally and grant only the minimum permission at the specific job.",
            )
        )

    return findings


def sarif(findings: Iterable[Finding]) -> dict:
    findings = list(findings)
    rules = {}
    for finding in findings:
        rules.setdefault(
            finding.rule_id,
            {
                "id": finding.rule_id,
                "name": finding.rule_id,
                "shortDescription": {"text": finding.message},
                "help": {"text": finding.remediation},
                "properties": {"security-severity": finding.severity},
            },
        )
    return {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "ClearGlass Artemis CI Guard",
                        "informationUri": "https://github.com/ClearGlasslabs/Opal-Koboi",
                        "rules": list(rules.values()),
                    }
                },
                "results": [
                    {
                        "ruleId": finding.rule_id,
                        "level": "error" if finding.severity in {"critical", "high"} else "warning",
                        "message": {"text": f"{finding.message} {finding.remediation}"},
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": finding.path},
                                    "region": {"startLine": finding.line},
                                }
                            }
                        ],
                    }
                    for finding in findings
                ],
            }
        ],
    }


def markdown(findings: list[Finding]) -> str:
    if not findings:
        return "## Artemis CI Guard\n\nNo supply-chain policy violations detected.\n"
    rows = [
        "## Artemis CI Guard",
        "",
        f"Detected **{len(findings)}** finding(s).",
        "",
        "| Severity | Rule | File | Line | Finding |",
        "|---|---|---|---:|---|",
    ]
    for finding in findings:
        message = finding.message.replace("|", "\\|")
        rows.append(
            f"| {finding.severity.upper()} | `{finding.rule_id}` | `{finding.path}` | "
            f"{finding.line} | {message} |"
        )
    rows.append("")
    return "\n".join(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--policy", default="security/ci-policy.json")
    parser.add_argument("--json-output", default="artemis-ci-guard.json")
    parser.add_argument("--sarif-output", default="artemis-ci-guard.sarif")
    parser.add_argument("--summary-output", default="")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    policy = json.loads((root / args.policy).read_text(encoding="utf-8"))
    workflow_dir = root / ".github" / "workflows"
    workflows = sorted((*workflow_dir.glob("*.yml"), *workflow_dir.glob("*.yaml")))
    if not workflows:
        print("No GitHub Actions workflows found.", file=sys.stderr)
        return 2

    findings = [
        finding
        for path in workflows
        for finding in scan_workflow(path.relative_to(root), policy)
    ]
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda finding: (
        severity_order[finding.severity], finding.path, finding.line, finding.rule_id
    ))

    (root / args.json_output).write_text(
        json.dumps([asdict(finding) for finding in findings], indent=2) + "\n",
        encoding="utf-8",
    )
    (root / args.sarif_output).write_text(
        json.dumps(sarif(findings), indent=2) + "\n", encoding="utf-8"
    )
    report = markdown(findings)
    if args.summary_output:
        (root / args.summary_output).write_text(report, encoding="utf-8")
    if summary_path := __import__("os").environ.get("GITHUB_STEP_SUMMARY"):
        with Path(summary_path).open("a", encoding="utf-8") as handle:
            handle.write(report)

    print(report)
    fail_on = set(policy.get("fail_on", ["critical", "high"]))
    return 1 if any(finding.severity in fail_on for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
