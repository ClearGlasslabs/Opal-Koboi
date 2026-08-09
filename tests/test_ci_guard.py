import tempfile
from pathlib import Path

from security.ci_guard import scan_workflow, workflow_events

POLICY = {"untrusted_events": [], "allowed_mutable_refs": [], "fail_on": ["critical", "high"]}

def _scan(workflow: str):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "workflow.yml"
        path.write_text(workflow, encoding="utf-8")
        return scan_workflow(path, POLICY)

def test_unnamed_checkout_step_requires_credential_opt_out():
    findings = _scan("""jobs:
  test:
    steps:
      - uses: actions/checkout@0123456789012345678901234567890123456789
      - run: echo test
""")
    assert [finding.rule_id for finding in findings] == ["CG-ACT-007"]

def test_unnamed_checkout_step_accepts_explicit_credential_opt_out():
    findings = _scan("""jobs:
  test:
    steps:
      - uses: actions/checkout@0123456789012345678901234567890123456789
        with:
          persist-credentials: false
      - run: echo test
""")
    assert findings == []


def test_workflow_events_do_not_treat_permissions_as_triggers():
    workflow = """on:
  schedule:
    - cron: '17 4 * * *'
  workflow_dispatch:
permissions:
  issues: write
  pull-requests: write
"""
    assert workflow_events(workflow) == {"schedule", "workflow_dispatch"}


def test_workflow_events_support_inline_event_lists():
    assert workflow_events("on: [push, pull_request]\n") == {"push", "pull_request"}
