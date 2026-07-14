from intelligence.entity_extractor import (
    FinancialAmountEntity,
    LLMEntityExtractor,
    OrganizationEntity,
    PersonEntity,
    enrich_evidence_with_llm_entities,
)

SAMPLE = """
CITY OF BURLINGTON Council Minutes March 4, 2024.
Mayor Marianne Meed Ward moved the motion. CAO Tim Commisso presented contract RFP-2023-14
awarded to 1234567 Ontario Inc. for $2.3M for downtown streetscaping.
"""


def extractor() -> LLMEntityExtractor:
    return LLMEntityExtractor(enable_local_fallback=True, max_retries=0)


def test_offline_fallback_is_explicit_and_auditable():
    result = extractor().extract(SAMPLE, document_id="burlington-2024-03-04")
    assert result.fallback_used is True
    assert result.prompt_hash
    assert result.system_prompt_hash
    assert result.tokens_used == 0
    assert result.document_id == "burlington-2024-03-04"


def test_extracts_people_and_normalized_amount():
    result = extractor().extract(SAMPLE)
    people = [entity for entity in result.entities if isinstance(entity, PersonEntity)]
    amounts = [entity for entity in result.entities if isinstance(entity, FinancialAmountEntity)]
    assert any(entity.name == "Marianne Meed Ward" and entity.is_elected_official for entity in people)
    assert any(entity.name == "Tim Commisso" and entity.is_senior_staff for entity in people)
    assert amounts[0].amount == 2_300_000
    assert amounts[0].amount_text == "$2.3M"


def test_numbered_company_post_validation():
    payload = {
        "entities": [{
            "entity_type": "ORGANIZATION",
            "name": "1234567 Ontario Inc.",
            "confidence": 0.95,
            "context_snippet": "awarded to 1234567 Ontario Inc. for downtown streetscaping",
        }]
    }
    from intelligence.entity_extractor import ExtractionPayload
    parsed = ExtractionPayload.model_validate(payload)
    entities, warnings = extractor()._post_validate(parsed, SAMPLE)
    organization = entities[0]
    assert isinstance(organization, OrganizationEntity)
    assert organization.is_numbered_company is True
    assert organization.org_type == "NUMBERED_COMPANY"
    assert isinstance(warnings, list)


def test_enriches_dict_evidence_without_replacing_existing_entities():
    evidence = {"id": "doc-1", "text": SAMPLE, "entities": [{"entity_type": "LEGACY", "name": "keep"}]}
    enriched = enrich_evidence_with_llm_entities(evidence, extractor())
    assert enriched is evidence
    assert enriched["entities"][0]["entity_type"] == "LEGACY"
    assert enriched["extraction_metadata"]["fallback_used"] is True
    assert enriched["extraction_metadata"]["summary"]


def test_rejects_empty_documents():
    try:
        extractor().extract("too short")
    except ValueError as exc:
        assert "at least 20" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
