"""Deterministic regulatory control overlay for ClearGlassInc Artemis.

This module does not attempt to make legal conclusions.  It converts a
deployment's counsel-approved data handling profile into machine-enforceable
obligations before an agent, model, or connector receives regulated data.
"""
from __future__ import annotations

import hashlib
import json
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Jurisdiction(StrEnum):
    UNITED_STATES = "US"
    NEW_YORK = "US-NY"
    CANADA = "CA"
    ONTARIO = "CA-ON"
    EUROPEAN_ECONOMIC_AREA = "EEA"


class DataCategory(StrEnum):
    PUBLIC = "public"
    PERSONAL = "personal"
    FINANCIAL = "financial"
    AUTHENTICATION = "authentication"
    INVESTIGATION = "investigation"


class ProcessingPurpose(StrEnum):
    FRAUD_PREVENTION = "fraud_prevention"
    AML_SCREENING = "aml_screening"
    CYBER_DEFENCE = "cyber_defence"
    CASE_INVESTIGATION = "case_investigation"
    MODEL_EVALUATION = "model_evaluation"
    MODEL_TRAINING = "model_training"


class RegulatoryProfile(StrictModel):
    """A versioned profile approved by privacy, security, and legal owners."""

    profile_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    allowed_purposes: set[ProcessingPurpose]
    allowed_processing_regions: set[Jurisdiction]
    retention_days: int = Field(gt=0)
    training_opt_in: bool = False
    require_encryption: bool = True
    require_immutable_audit: bool = True


class ProcessingRequest(StrictModel):
    request_id: str = Field(min_length=1)
    mission_id: str = Field(min_length=1)
    purpose: ProcessingPurpose
    categories: set[DataCategory]
    subject_jurisdictions: set[Jurisdiction]
    processing_region: Jurisdiction
    external_model: bool = False
    retention_days: int = Field(gt=0)


class RegulatoryDecision(StrictModel):
    allowed: bool
    reasons: list[str]
    obligations: list[str]
    decision_hash: str


def _decision_hash(profile: RegulatoryProfile, request: ProcessingRequest, reasons: list[str]) -> str:
    payload = {
        "profile": profile.model_dump(mode="json"),
        "request": request.model_dump(mode="json"),
        "reasons": reasons,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode()).hexdigest()


def evaluate_regulatory_controls(
    profile: RegulatoryProfile,
    request: ProcessingRequest,
) -> RegulatoryDecision:
    """Fail closed and return obligations for an execution gateway to enforce."""

    reasons: list[str] = []
    obligations = [
        f"attach regulatory_profile={profile.profile_id}@{profile.version}",
        "record purpose, data categories, region, and decision in immutable audit",
        "propagate deletion deadline to every derived object and embedding",
    ]

    if request.purpose not in profile.allowed_purposes:
        reasons.append("processing purpose is not approved by the regulatory profile")
    if request.processing_region not in profile.allowed_processing_regions:
        reasons.append("processing region is not approved by the regulatory profile")
    if request.retention_days > profile.retention_days:
        reasons.append("requested retention exceeds the approved maximum")
    if request.purpose == ProcessingPurpose.MODEL_TRAINING and not profile.training_opt_in:
        reasons.append("regulated data is not approved for model training")
    if request.external_model and DataCategory.AUTHENTICATION in request.categories:
        reasons.append("authentication data may not be sent to an external model")

    if DataCategory.PERSONAL in request.categories or DataCategory.FINANCIAL in request.categories:
        obligations.extend(
            [
                "apply field-level minimization before retrieval",
                "bind output to the originating mission and subject rights workflow",
                "prevent prompt and response persistence outside approved stores",
            ]
        )
    if profile.require_encryption:
        obligations.append("enforce mTLS in transit and tenant-scoped KMS encryption at rest")
    if request.external_model:
        obligations.append("use a no-training provider route with a counsel-approved data processing agreement")

    return RegulatoryDecision(
        allowed=not reasons,
        reasons=reasons or ["counsel-approved profile checks passed"],
        obligations=obligations,
        decision_hash=_decision_hash(profile, request, reasons),
    )
