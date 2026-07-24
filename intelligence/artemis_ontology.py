"""Mission-scoped ontology primitives for ClearGlassInc Artemis.

This module is intentionally storage-agnostic.  The same validated records can
back a Foundry Ontology action, a Gotham investigation view, or a local test
double.  Authorization is evaluated before text matching so callers cannot use
search terms to infer the existence of inaccessible entities.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import IntEnum, StrEnum
from typing import Iterable

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Classification(IntEnum):
    UNCLASSIFIED = 0
    PROTECTED = 1
    CONFIDENTIAL = 2
    SECRET = 3
    TOP_SECRET = 4


class EntityType(StrEnum):
    PERSON = "person"
    ORGANIZATION = "organization"
    INFRASTRUCTURE = "infrastructure"
    ASSET = "asset"
    ACCOUNT = "account"
    LOCATION = "location"
    DEVICE = "device"


class EvidenceRef(StrictModel):
    evidence_id: str = Field(min_length=1)
    source_uri: str = Field(min_length=1)
    content_hash: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    observed_at: datetime
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode="after")
    def ingestion_cannot_precede_observation(self) -> "EvidenceRef":
        if self.ingested_at < self.observed_at:
            raise ValueError("ingested_at cannot precede observed_at")
        return self


class AccessMarkings(StrictModel):
    classification: Classification
    compartments: frozenset[str] = Field(default_factory=frozenset)
    releasable_to: frozenset[str] = Field(min_length=1)

    @field_validator("compartments", "releasable_to")
    @classmethod
    def normalize_markings(cls, values: frozenset[str]) -> frozenset[str]:
        normalized = frozenset(value.upper() for value in values if value)
        if len(normalized) != len(values):
            raise ValueError("access markings cannot be blank")
        return normalized


class TemporalWindow(StrictModel):
    valid_from: datetime
    valid_to: datetime | None = None

    @model_validator(mode="after")
    def window_is_ordered(self) -> "TemporalWindow":
        if self.valid_to is not None and self.valid_to <= self.valid_from:
            raise ValueError("valid_to must be later than valid_from")
        return self

    def contains(self, instant: datetime) -> bool:
        return self.valid_from <= instant and (self.valid_to is None or instant < self.valid_to)


class OntologyEntity(StrictModel):
    entity_id: str = Field(min_length=1)
    entity_type: EntityType
    canonical_name: str = Field(min_length=1)
    aliases: tuple[str, ...] = ()
    mission_ids: frozenset[str] = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    temporal: TemporalWindow
    access: AccessMarkings
    evidence: tuple[EvidenceRef, ...] = Field(min_length=1)
    attributes: dict[str, str | int | float | bool] = Field(default_factory=dict)


class OntologyRelationship(StrictModel):
    relationship_id: str = Field(min_length=1)
    source_entity_id: str = Field(min_length=1)
    target_entity_id: str = Field(min_length=1)
    relationship_type: str = Field(min_length=1)
    mission_ids: frozenset[str] = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    temporal: TemporalWindow
    access: AccessMarkings
    evidence: tuple[EvidenceRef, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def endpoints_must_differ(self) -> "OntologyRelationship":
        if self.source_entity_id == self.target_entity_id:
            raise ValueError("relationship endpoints must differ")
        return self


class QueryContext(StrictModel):
    actor_id: str = Field(min_length=1)
    mission_id: str = Field(min_length=1)
    assigned_mission_ids: frozenset[str] = Field(min_length=1)
    clearance: Classification
    compartments: frozenset[str] = Field(default_factory=frozenset)
    coalition: str = Field(min_length=1)
    purpose: str = Field(min_length=1)

    @field_validator("coalition")
    @classmethod
    def normalize_coalition(cls, value: str) -> str:
        return value.upper()

    @field_validator("compartments")
    @classmethod
    def normalize_compartments(cls, values: frozenset[str]) -> frozenset[str]:
        return frozenset(value.upper() for value in values)

    @model_validator(mode="after")
    def mission_must_be_assigned(self) -> "QueryContext":
        if self.mission_id not in self.assigned_mission_ids:
            raise ValueError("active mission must be assigned to actor")
        return self


class EntityQuery(StrictModel):
    text: str | None = None
    entity_types: frozenset[EntityType] = Field(default_factory=frozenset)
    minimum_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    as_of: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    limit: int = Field(default=50, ge=1, le=200)


class OntologyQueryResult(StrictModel):
    entities: tuple[OntologyEntity, ...]
    relationships: tuple[OntologyRelationship, ...]
    query_hash: str
    evaluated_at: datetime


def _is_authorized(context: QueryContext, missions: frozenset[str], access: AccessMarkings) -> bool:
    return (
        context.mission_id in missions
        and context.clearance >= access.classification
        and access.compartments.issubset(context.compartments)
        and context.coalition in access.releasable_to
    )


class InMemoryOntologyStore:
    """Deterministic reference adapter for policy-filtered ontology queries."""

    def __init__(
        self,
        entities: Iterable[OntologyEntity] = (),
        relationships: Iterable[OntologyRelationship] = (),
    ) -> None:
        self._entities = self._index_unique(entities, "entity_id")
        self._relationships = self._index_unique(relationships, "relationship_id")
        for relationship in self._relationships.values():
            if relationship.source_entity_id not in self._entities or relationship.target_entity_id not in self._entities:
                raise ValueError(f"relationship {relationship.relationship_id} references an unknown entity")

    @staticmethod
    def _index_unique(records: Iterable[StrictModel], key: str) -> dict[str, StrictModel]:
        indexed: dict[str, StrictModel] = {}
        for record in records:
            identifier = str(getattr(record, key))
            if identifier in indexed:
                raise ValueError(f"duplicate {key}: {identifier}")
            indexed[identifier] = record
        return indexed

    def query(self, context: QueryContext, query: EntityQuery) -> OntologyQueryResult:
        """Return only authorized, temporally valid records and their visible edges."""

        needle = query.text.casefold() if query.text else None
        visible: list[OntologyEntity] = []
        for entity in self._entities.values():
            if not _is_authorized(context, entity.mission_ids, entity.access):
                continue
            if not entity.temporal.contains(query.as_of) or entity.confidence < query.minimum_confidence:
                continue
            if query.entity_types and entity.entity_type not in query.entity_types:
                continue
            names = (entity.canonical_name, *entity.aliases)
            if needle and not any(needle in name.casefold() for name in names):
                continue
            visible.append(entity)

        visible.sort(key=lambda item: (-item.confidence, item.entity_id))
        visible = visible[: query.limit]
        visible_ids = {entity.entity_id for entity in visible}
        edges = tuple(
            relationship
            for relationship in self._relationships.values()
            if relationship.source_entity_id in visible_ids
            and relationship.target_entity_id in visible_ids
            and relationship.temporal.contains(query.as_of)
            and _is_authorized(context, relationship.mission_ids, relationship.access)
        )
        evaluated_at = datetime.now(timezone.utc)
        canonical_query = {
            "actor_id": context.actor_id,
            "mission_id": context.mission_id,
            "purpose": context.purpose,
            "query": query.model_dump(mode="json"),
        }
        query_hash = hashlib.sha256(
            json.dumps(canonical_query, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        return OntologyQueryResult(
            entities=tuple(visible),
            relationships=edges,
            query_hash=f"sha256:{query_hash}",
            evaluated_at=evaluated_at,
        )
