from datetime import datetime, timezone

import pytest

from intelligence.artemis_ontology import (
    AccessMarkings,
    Classification,
    EntityQuery,
    EntityType,
    EvidenceRef,
    InMemoryOntologyStore,
    OntologyEntity,
    OntologyRelationship,
    QueryContext,
    TemporalWindow,
)

NOW = datetime(2026, 7, 24, 12, tzinfo=timezone.utc)
HASH = "sha256:" + "a" * 64


def evidence() -> tuple[EvidenceRef, ...]:
    return (
        EvidenceRef(
            evidence_id="ev-1",
            source_uri="foundry://dataset/intel-normalized/row-1",
            content_hash=HASH,
            observed_at=NOW,
            ingested_at=NOW,
        ),
    )


def markings(*, coalition: frozenset[str] = frozenset({"CAN", "USA"})) -> AccessMarkings:
    return AccessMarkings(
        classification=Classification.SECRET,
        compartments=frozenset({"ARTEMIS"}),
        releasable_to=coalition,
    )


def entity(entity_id: str, name: str, **overrides) -> OntologyEntity:
    values = {
        "entity_id": entity_id,
        "entity_type": EntityType.ORGANIZATION,
        "canonical_name": name,
        "aliases": (),
        "mission_ids": frozenset({"mission-northstar"}),
        "confidence": 0.9,
        "temporal": TemporalWindow(valid_from=NOW),
        "access": markings(),
        "evidence": evidence(),
    }
    values.update(overrides)
    return OntologyEntity(**values)


def context(**overrides) -> QueryContext:
    values = {
        "actor_id": "analyst-17",
        "mission_id": "mission-northstar",
        "assigned_mission_ids": frozenset({"mission-northstar"}),
        "clearance": Classification.SECRET,
        "compartments": frozenset({"ARTEMIS"}),
        "coalition": "can",
        "purpose": "alert_triage",
    }
    values.update(overrides)
    return QueryContext(**values)


def test_query_filters_before_matching_and_returns_visible_relationships():
    alpha = entity("ent-alpha", "Alpha Logistics", aliases=("A-Log",))
    beta = entity("ent-beta", "Beta Port")
    hidden = entity("ent-hidden", "Alpha Restricted", access=markings(coalition=frozenset({"GBR"})))
    edge = OntologyRelationship(
        relationship_id="rel-1",
        source_entity_id=alpha.entity_id,
        target_entity_id=beta.entity_id,
        relationship_type="SUPPLIES",
        mission_ids=frozenset({"mission-northstar"}),
        confidence=0.83,
        temporal=TemporalWindow(valid_from=NOW),
        access=markings(),
        evidence=evidence(),
    )
    store = InMemoryOntologyStore([alpha, beta, hidden], [edge])

    result = store.query(context(), EntityQuery(as_of=NOW))

    assert [item.entity_id for item in result.entities] == ["ent-alpha", "ent-beta"]
    assert [item.relationship_id for item in result.relationships] == ["rel-1"]
    assert result.query_hash.startswith("sha256:")


def test_query_enforces_mission_clearance_compartment_and_release_marking():
    store = InMemoryOntologyStore([entity("ent-1", "Visible only with all markings")])

    assert not store.query(context(clearance=Classification.CONFIDENTIAL), EntityQuery(as_of=NOW)).entities
    assert not store.query(context(compartments=frozenset()), EntityQuery(as_of=NOW)).entities
    assert not store.query(context(coalition="GBR"), EntityQuery(as_of=NOW)).entities
    assert not store.query(
        context(mission_id="mission-other", assigned_mission_ids=frozenset({"mission-other"})),
        EntityQuery(as_of=NOW),
    ).entities


def test_query_is_temporal_confidence_filtered_and_deterministic():
    expired = entity(
        "ent-expired",
        "Old Alpha",
        temporal=TemporalWindow(valid_from=datetime(2025, 1, 1, tzinfo=timezone.utc), valid_to=NOW),
    )
    active = entity("ent-active", "Alpha Current", confidence=0.95)
    low_confidence = entity("ent-low", "Alpha Rumor", confidence=0.2)
    store = InMemoryOntologyStore([expired, active, low_confidence])
    query = EntityQuery(text="alpha", minimum_confidence=0.8, as_of=NOW)

    first = store.query(context(), query)
    second = store.query(context(), query)

    assert [item.entity_id for item in first.entities] == ["ent-active"]
    assert first.query_hash == second.query_hash


def test_context_rejects_unassigned_active_mission():
    with pytest.raises(ValueError, match="active mission must be assigned"):
        context(assigned_mission_ids=frozenset({"mission-other"}))


def test_store_rejects_dangling_relationships():
    alpha = entity("ent-alpha", "Alpha")
    dangling = OntologyRelationship(
        relationship_id="rel-dangling",
        source_entity_id=alpha.entity_id,
        target_entity_id="ent-missing",
        relationship_type="RELATED_TO",
        mission_ids=frozenset({"mission-northstar"}),
        confidence=0.5,
        temporal=TemporalWindow(valid_from=NOW),
        access=markings(),
        evidence=evidence(),
    )

    with pytest.raises(ValueError, match="references an unknown entity"):
        InMemoryOntologyStore([alpha], [dangling])


def test_evidence_rejects_impossible_lineage_time():
    with pytest.raises(ValueError, match="ingested_at cannot precede observed_at"):
        EvidenceRef(
            evidence_id="ev-invalid",
            source_uri="foundry://dataset/source/row",
            content_hash=HASH,
            observed_at=NOW,
            ingested_at=datetime(2026, 7, 23, tzinfo=timezone.utc),
        )
