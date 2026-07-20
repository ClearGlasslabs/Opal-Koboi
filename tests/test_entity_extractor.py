from __future__ import annotations

import json

import pytest

from intelligence.entity_extractor import (
    ExtractionPayload,
    FinancialAmountEntity,
    LLMEntityExtractor,
    OrganizationEntity,
    PersonEntity,
    enrich_evidence_with_llm_entities,
)
from intelligence.financial_watchdog_agent import run

SAMPLE = """
CITY OF BURLINGTON Council Minutes March 4, 2024.
Mayor Marianne Meed Ward moved the motion. CAO Tim Commisso presented contract RFP-2023-14
awarded to 1234567 Ontario Inc. for $2.3M for downtown streetscaping.
"""


def extractor(**overrides) -> LLMEntityExtractor:
    options = {
        "enable_local_fallback": True,
        "max_retries": 0,
        "retry_backoff_seconds": 0,
    }
    options.update(overrides)
    return LLMEntityExtractor(**options)


def test_offline_fallback_is_explicit_and_auditable():
    result = extractor().extract(SAMPLE, document_id="burlington-2024-03-04")
    assert result.fallback_used is True
    assert result.prompt_hash
    assert result.prompt_template_hash
    assert result.system_prompt_hash
    assert result.schema_hash
    assert result.document_sha256
    assert result.tokens_used == 0
    assert result.document_id == "burlington-2024-03-04"
    assert result.attempts == 1
    assert result.source_characters == len(SAMPLE)


def test_extracts_people_and_normalized_amount():
    result = extractor().extract(SAMPLE)
    people = [entity for entity in result.entities if isinstance(entity, PersonEntity)]
    amounts = [entity for entity in result.entities if isinstance(entity, FinancialAmountEntity)]
    assert any(entity.name == "Marianne Meed Ward" and entity.is_elected_official for entity in people)
    assert any(entity.name == "Tim Commisso" and entity.is_senior_staff for entity in people)
    assert amounts[0].amount == 2_300_000
    assert amounts[0].amount_text == "$2.3M"


def test_numbered_company_post_validation():
    snippet = "contract RFP-2023-14 awarded to 1234567 Ontario Inc. for $2.3M for downtown streetscaping"
    payload = ExtractionPayload.model_validate({
        "entities": [{
            "entity_type": "ORGANIZATION",
            "name": "1234567 Ontario Inc.",
            "confidence": 0.95,
            "context_snippet": snippet,
        }]
    })
    entities, warnings = extractor()._post_validate(payload, SAMPLE)
    organization = entities[0]
    assert isinstance(organization, OrganizationEntity)
    assert organization.is_numbered_company is True
    assert organization.org_type == "NUMBERED_COMPANY"
    assert isinstance(warnings, list)


def test_strict_grounding_drops_hallucinated_entity():
    payload = ExtractionPayload.model_validate({
        "entities": [{
            "entity_type": "PERSON",
            "name": "Invented Person",
            "confidence": 0.99,
            "context_snippet": "Invented Person approved a secret payment that never appears in this source",
        }]
    })
    entities, warnings = extractor(strict_grounding=True)._post_validate(payload, SAMPLE)
    assert entities == []
    assert any("Ungrounded entity dropped" in warning for warning in warnings)


def test_compatible_provider_routes_to_json_path(monkeypatch):
    instance = extractor(
        provider="compatible",
        base_url="http://localhost:11434/v1",
        api_key=None,
        enable_local_fallback=False,
    )
    called = {"compatible": False}

    def fake_call(prompt: str):
        called["compatible"] = True
        assert "Document Text" in prompt
        return ExtractionPayload(entities=[]), 17

    monkeypatch.setattr(instance, "_call_compatible", fake_call)
    result = instance.extract(SAMPLE)
    assert called["compatible"] is True
    assert result.provider == "compatible"
    assert result.tokens_used == 17
    assert result.fallback_used is False


def test_enriches_dict_evidence_without_replacing_existing_entities():
    evidence = {"id": "doc-1", "text": SAMPLE, "entities": [{"entity_type": "LEGACY", "name": "keep"}]}
    enriched = enrich_evidence_with_llm_entities(evidence, extractor())
    assert enriched is evidence
    assert enriched["entities"][0]["entity_type"] == "LEGACY"
    assert enriched["extraction_metadata"]["fallback_used"] is True
    assert enriched["extraction_metadata"]["summary"]


def test_batch_preserves_input_order():
    docs = [
        {"id": "a", "text": SAMPLE},
        {"id": "b", "text": SAMPLE.replace("$2.3M", "$4M")},
    ]
    results = extractor().extract_batch(docs, max_workers=2)
    assert [result.document_id for result in results] == ["a", "b"]


def test_truncation_is_recorded():
    long_text = "Mayor Jane Doe approved the contract. " * 500
    result = extractor().extract(long_text)
    assert result.truncated is True
    assert result.submitted_characters <= 12_020


def test_cli_writes_json_with_explicit_dev_fallback(tmp_path):
    source = tmp_path / "minutes.txt"
    output = tmp_path / "result.json"
    source.write_text(SAMPLE, encoding="utf-8")
    code = run([
        str(source),
        "--output",
        str(output),
        "--document-id",
        "doc-cli",
        "--allow-dev-fallback",
        "--max-retries",
        "0",
    ])
    assert code == 0
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["document_id"] == "doc-cli"
    assert data["fallback_used"] is True


def test_rejects_empty_documents():
    with pytest.raises(ValueError, match="at least 20"):
        extractor().extract("too short")
