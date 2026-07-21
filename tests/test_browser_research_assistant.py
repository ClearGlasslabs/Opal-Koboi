import pytest
from pydantic import ValidationError

from intelligence.browser_research_assistant import (
    BrowserAction,
    BrowserRole,
    LocalFirstVault,
    ResearchSource,
    authorize_browser_action,
    build_cited_summary,
    source_hash,
)


def test_osint_source_requires_public_https():
    with pytest.raises(ValidationError):
        ResearchSource(url="http://localhost/admin", title="Local", content_sha256="a" * 64)


def test_cited_summary_requires_citation_per_claim():
    src = ResearchSource(url="https://example.gov/advisory", title="Advisory", content_sha256=source_hash("patched"))
    summary = build_cited_summary([("Vendor advisory confirms a patched vulnerability", src, "patched vulnerability")])
    assert summary.citations[0].source_hash == source_hash("patched")


def test_vault_round_trip_and_tamper_detection():
    vault = LocalFirstVault("correct horse battery staple")
    envelope = vault.encrypt("api-token")
    assert vault.decrypt(envelope) == "api-token"
    envelope["ciphertext"] = "AAAA"
    with pytest.raises(ValueError):
        vault.decrypt(envelope)


def test_browser_rbac_audit_events_are_sealed():
    event = authorize_browser_action(BrowserRole.VIEWER, BrowserAction.MANAGE_SECRETS, "usr_1", "vault")
    assert not event.allowed
    assert event.event_hash
