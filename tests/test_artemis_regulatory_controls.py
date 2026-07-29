from intelligence.artemis_regulatory_controls import (
    DataCategory,
    Jurisdiction,
    ProcessingPurpose,
    ProcessingRequest,
    RegulatoryProfile,
    evaluate_regulatory_controls,
)


def profile(**overrides) -> RegulatoryProfile:
    values = {
        "profile_id": "financial-intelligence",
        "version": "2026.07",
        "allowed_purposes": {ProcessingPurpose.FRAUD_PREVENTION, ProcessingPurpose.MODEL_EVALUATION},
        "allowed_processing_regions": {Jurisdiction.CANADA, Jurisdiction.ONTARIO},
        "retention_days": 365,
    }
    values.update(overrides)
    return RegulatoryProfile(**values)


def request(**overrides) -> ProcessingRequest:
    values = {
        "request_id": "req-001",
        "mission_id": "mis-fincrime",
        "purpose": ProcessingPurpose.FRAUD_PREVENTION,
        "categories": {DataCategory.PERSONAL, DataCategory.FINANCIAL},
        "subject_jurisdictions": {Jurisdiction.ONTARIO},
        "processing_region": Jurisdiction.CANADA,
        "retention_days": 90,
    }
    values.update(overrides)
    return ProcessingRequest(**values)


def test_allows_profiled_processing_and_emits_enforceable_obligations():
    decision = evaluate_regulatory_controls(profile(), request())

    assert decision.allowed is True
    assert decision.decision_hash
    assert "apply field-level minimization before retrieval" in decision.obligations
    assert "propagate deletion deadline to every derived object and embedding" in decision.obligations


def test_denies_unapproved_cross_border_region_and_excess_retention():
    decision = evaluate_regulatory_controls(
        profile(),
        request(processing_region=Jurisdiction.NEW_YORK, retention_days=730),
    )

    assert decision.allowed is False
    assert "processing region is not approved by the regulatory profile" in decision.reasons
    assert "requested retention exceeds the approved maximum" in decision.reasons


def test_denies_training_without_explicit_profile_opt_in():
    decision = evaluate_regulatory_controls(
        profile(allowed_purposes={ProcessingPurpose.MODEL_TRAINING}),
        request(purpose=ProcessingPurpose.MODEL_TRAINING),
    )

    assert decision.allowed is False
    assert "regulated data is not approved for model training" in decision.reasons


def test_denies_external_model_route_for_authentication_data():
    decision = evaluate_regulatory_controls(
        profile(),
        request(categories={DataCategory.AUTHENTICATION}, external_model=True),
    )

    assert decision.allowed is False
    assert "authentication data may not be sent to an external model" in decision.reasons
