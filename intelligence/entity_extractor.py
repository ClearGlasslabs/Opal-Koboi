"""ClearGlass Financial Influence Watchdog v2.1.

Auditable, provider-neutral LLM entity extraction for Ontario and Canadian
public-governance documents.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import time
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Annotated, Literal, Optional, Union

from pydantic import BaseModel, Field, TypeAdapter, field_validator

logger = logging.getLogger(__name__)
PROMPT_VERSION = "v2.1.0-governance-ca-2026-07-11"
MAX_DOCUMENT_CHARS = 12_000

SYSTEM_PROMPT = """You are a forensic entity extraction specialist for Canadian public-sector accountability.
Extract only entities relevant to financial-influence detection in Ontario municipal and provincial governance.
Every entity must be grounded in verbatim source text. Never infer a role, affiliation, amount, date, or relationship.
Return one unique record per entity. Include an exact 10-30 word context_snippet and confidence from 0.0 to 1.0.
Normalize financial amounts numerically while preserving amount_text. Use CAD unless another currency is explicit.
Recognize elected officials, senior staff, lobbyists, bidders, developers, numbered companies, contracts, procurement IDs,
decision dates, and Ontario statutes/bylaws/policies. Output valid JSON matching the supplied schema and no prose."""

USER_PROMPT = """Document Metadata:
- Title: {title}
- Source Type: {source_type}
- Jurisdiction: {jurisdiction}
- Retrieved At: {retrieved_at}
- Document ID: {document_id}

Document Text:
---
{document_text}
---
Extract all influence-relevant entities. Return JSON with key \"entities\"."""


class ExtractedEntity(BaseModel):
    entity_type: str
    name: str
    confidence: float = Field(ge=0.0, le=1.0)
    context_snippet: str
    start_char: Optional[int] = Field(default=None, ge=0)
    end_char: Optional[int] = Field(default=None, ge=0)
    extraction_notes: Optional[str] = None


class PersonEntity(ExtractedEntity):
    entity_type: Literal["PERSON"] = "PERSON"
    role: Optional[str] = None
    organization: Optional[str] = None
    ward: Optional[str] = None
    is_elected_official: bool = False
    is_senior_staff: bool = False
    is_lobbyist: bool = False


class OrganizationEntity(ExtractedEntity):
    entity_type: Literal["ORGANIZATION"] = "ORGANIZATION"
    org_type: Literal[
        "BIDDER", "DEVELOPER", "LOBBY_FIRM", "MUNICIPAL_DEPT",
        "PROVINCIAL_BODY", "NUMBERED_COMPANY", "NONPROFIT", "OTHER"
    ] = "OTHER"
    registration_number: Optional[str] = None
    is_numbered_company: bool = False


class FinancialAmountEntity(ExtractedEntity):
    entity_type: Literal["FINANCIAL_AMOUNT"] = "FINANCIAL_AMOUNT"
    amount: float = Field(ge=0)
    currency: str = "CAD"
    amount_text: str
    is_contract_value: bool = False
    is_campaign_contribution: bool = False
    context: Literal["CONTRACT", "BUDGET", "CONTRIBUTION", "FINE", "GRANT", "OTHER"] = "OTHER"


class ContractEntity(ExtractedEntity):
    entity_type: Literal["CONTRACT"] = "CONTRACT"
    contract_id: Optional[str] = None
    title: Optional[str] = None
    vendor_name: Optional[str] = None
    buyer_name: Optional[str] = None
    value_amount: Optional[float] = Field(default=None, ge=0)


class DateEntity(ExtractedEntity):
    entity_type: Literal["DATE"] = "DATE"
    date_text: str
    iso_date: Optional[str] = None
    date_type: Literal["DECISION_DATE", "MEETING_DATE", "AWARD_DATE", "FILING_DATE", "DEADLINE", "OTHER"] = "OTHER"

    @field_validator("iso_date")
    @classmethod
    def validate_iso_date(cls, value: Optional[str]) -> Optional[str]:
        if value:
            datetime.strptime(value, "%Y-%m-%d")
        return value


class PolicyEntity(ExtractedEntity):
    entity_type: Literal["POLICY"] = "POLICY"
    act_name: Optional[str] = None
    section_reference: Optional[str] = None
    jurisdiction: str = "Ontario"
    policy_type: Literal["STATUTE", "BYLAW", "POLICY", "REGULATION", "MOTION"] = "STATUTE"

    @field_validator("act_name")
    @classmethod
    def normalize_act(cls, value: Optional[str]) -> Optional[str]:
        if not value:
            return value
        aliases = {
            "municipal act": "Municipal Act, 2001",
            "planning act": "Planning Act",
            "greenbelt": "Greenbelt Act, 2005",
            "mfippa": "Municipal Freedom of Information and Protection of Privacy Act",
        }
        lower = value.lower()
        return next((canonical for key, canonical in aliases.items() if key in lower), value)


AnyInfluenceEntity = Annotated[
    Union[PersonEntity, OrganizationEntity, FinancialAmountEntity, ContractEntity, DateEntity, PolicyEntity],
    Field(discriminator="entity_type"),
]
_ENTITY_ADAPTER = TypeAdapter(AnyInfluenceEntity)


class ExtractionPayload(BaseModel):
    entities: list[AnyInfluenceEntity] = Field(default_factory=list)


class ExtractionResult(BaseModel):
    model_config = {"protected_namespaces": ()}
    entities: list[AnyInfluenceEntity]
    model_name: str
    provider: str
    prompt_version: str
    prompt_hash: str
    system_prompt_hash: str
    tokens_used: Optional[int] = None
    latency_ms: Optional[float] = None
    extraction_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    document_id: Optional[str] = None
    document_metadata: dict[str, Any] = Field(default_factory=dict)
    validation_warnings: list[str] = Field(default_factory=list)
    fallback_used: bool = False

    def to_evidence_entities(self) -> list[dict[str, Any]]:
        return [entity.model_dump() for entity in self.entities]

    def summary(self) -> dict[str, int]:
        return dict(Counter(entity.entity_type for entity in self.entities))


class LLMEntityExtractor:
    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        provider: Literal["auto", "openai", "anthropic", "compatible"] = "auto",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        prompt_version: str = PROMPT_VERSION,
        temperature: float = 0.0,
        max_retries: int = 2,
        enable_local_fallback: bool = False,
    ) -> None:
        self.model_name = model_name
        self.provider = self._resolve_provider(provider, model_name)
        self.api_key = api_key or self._provider_key(self.provider)
        self.base_url = base_url
        self.prompt_version = prompt_version
        self.temperature = temperature
        self.max_retries = max(0, max_retries)
        self.enable_local_fallback = enable_local_fallback
        self.system_prompt_hash = self._hash(SYSTEM_PROMPT)
        self.prompt_hash = self._hash(SYSTEM_PROMPT + USER_PROMPT + prompt_version)

    @staticmethod
    def _hash(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def _resolve_provider(provider: str, model_name: str) -> str:
        if provider != "auto":
            return provider
        return "anthropic" if "claude" in model_name.lower() else "openai"

    @staticmethod
    def _provider_key(provider: str) -> Optional[str]:
        env = "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY"
        return os.getenv(env) or (os.getenv("GROQ_API_KEY") if provider == "compatible" else None)

    def _build_user_prompt(self, text: str, metadata: dict[str, Any]) -> str:
        clean = text.strip()
        if len(clean) > MAX_DOCUMENT_CHARS:
            clean = clean[:MAX_DOCUMENT_CHARS].rsplit(" ", 1)[0] + "\n...[TRUNCATED]"
        return USER_PROMPT.format(
            title=metadata.get("title", "Untitled"),
            source_type=metadata.get("source_type", "unknown"),
            jurisdiction=metadata.get("jurisdiction", "Ontario"),
            retrieved_at=metadata.get("retrieved_at", datetime.now(timezone.utc).isoformat()),
            document_id=metadata.get("document_id", "unknown"),
            document_text=clean,
        )

    def _call_openai(self, user_prompt: str) -> tuple[ExtractionPayload, Optional[int]]:
        from openai import OpenAI
        kwargs = {k: v for k, v in {"api_key": self.api_key, "base_url": self.base_url}.items() if v}
        client = OpenAI(**kwargs)
        completion = client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}],
            response_format=ExtractionPayload,
            temperature=self.temperature,
        )
        payload = completion.choices[0].message.parsed
        if payload is None:
            raise ValueError("Provider returned no parsed structured output")
        return payload, completion.usage.total_tokens if completion.usage else None

    def _call_anthropic(self, user_prompt: str) -> tuple[ExtractionPayload, Optional[int]]:
        import anthropic
        client = anthropic.Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model=self.model_name,
            max_tokens=4096,
            temperature=self.temperature,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt + "\nReturn JSON only."}],
        )
        text = "".join(block.text for block in response.content if getattr(block, "type", "") == "text")
        match = re.search(r"\{.*\}", text, re.DOTALL)
        payload = ExtractionPayload.model_validate_json(match.group(0) if match else text)
        usage = getattr(response, "usage", None)
        tokens = (usage.input_tokens + usage.output_tokens) if usage else None
        return payload, tokens

    def _simulate(self, text: str) -> ExtractionPayload:
        entities: list[AnyInfluenceEntity] = []
        for match in re.finditer(r"\$\s?([\d,]+(?:\.\d{1,2})?)\s*([MK]?)\b", text, re.I):
            raw, suffix = match.group(0), match.group(2).upper()
            amount = float(match.group(1).replace(",", "")) * ({"M": 1_000_000, "K": 1_000}.get(suffix, 1))
            snippet = self._snippet(text, match.start(), match.end())
            entities.append(FinancialAmountEntity(name=raw, confidence=0.8, context_snippet=snippet,
                start_char=match.start(), end_char=match.end(), amount=amount, amount_text=raw,
                is_contract_value="contract" in snippet.lower(), context="CONTRACT" if "contract" in snippet.lower() else "OTHER"))
        role_pattern = re.compile(r"\b(Mayor|Councillor|Councilor|CAO|City Manager|Clerk|Regional Chair|Director of [A-Za-z &]+)\s+([A-Z][A-Za-z'’-]+(?:\s+[A-Z][A-Za-z'’-]+){1,2})")
        for match in role_pattern.finditer(text):
            role, name = match.groups()
            lower = role.lower()
            entities.append(PersonEntity(name=name, confidence=0.85, context_snippet=self._snippet(text, match.start(), match.end()),
                start_char=match.start(), end_char=match.end(), role=role,
                is_elected_official=any(x in lower for x in ("mayor", "councillor", "councilor")),
                is_senior_staff=any(x in lower for x in ("cao", "manager", "director", "clerk"))))
        return ExtractionPayload(entities=entities)

    @staticmethod
    def _snippet(text: str, start: int, end: int, radius: int = 90) -> str:
        return " ".join(text[max(0, start-radius):min(len(text), end+radius)].split())

    def _post_validate(self, payload: ExtractionPayload, source_text: str) -> tuple[list[AnyInfluenceEntity], list[str]]:
        warnings: list[str] = []
        output: list[AnyInfluenceEntity] = []
        seen: set[tuple[str, str]] = set()
        for entity in payload.entities:
            key = (entity.entity_type, entity.name.casefold().strip())
            if key in seen:
                warnings.append(f"Duplicate removed: {entity.entity_type}:{entity.name}")
                continue
            seen.add(key)
            if entity.context_snippet not in source_text:
                normalized_source = " ".join(source_text.split())
                normalized_snippet = " ".join(entity.context_snippet.split())
                if normalized_snippet not in normalized_source:
                    warnings.append(f"Ungrounded snippet: {entity.entity_type}:{entity.name}")
                    entity.confidence = min(entity.confidence, 0.5)
            if entity.start_char is not None and entity.end_char is not None and entity.start_char > entity.end_char:
                warnings.append(f"Invalid offsets cleared: {entity.entity_type}:{entity.name}")
                entity.start_char = entity.end_char = None
            if isinstance(entity, FinancialAmountEntity) and entity.amount > 10_000_000_000:
                warnings.append(f"Large amount requires review: {entity.amount_text}")
                entity.confidence = min(entity.confidence, 0.6)
            if isinstance(entity, OrganizationEntity) and re.match(r"^\d{6,9}\s+(?:ONTARIO|CANADA)?\s*(?:INC|CORP|LTD|LIMITED)\.?$", entity.name.upper()):
                entity.is_numbered_company = True
                entity.org_type = "NUMBERED_COMPANY"
            output.append(_ENTITY_ADAPTER.validate_python(entity))
        return output, warnings

    def extract(self, document_text: str, document_id: Optional[str] = None,
                metadata: Optional[dict[str, Any]] = None) -> ExtractionResult:
        if len(document_text.strip()) < 20:
            raise ValueError("document_text must contain at least 20 non-whitespace characters")
        meta = dict(metadata or {})
        meta["document_id"] = document_id or meta.get("document_id", "unknown")
        meta.setdefault("title", meta["document_id"])
        meta.setdefault("source_type", "council_minutes")
        user_prompt = self._build_user_prompt(document_text, meta)
        payload: Optional[ExtractionPayload] = None
        tokens: Optional[int] = None
        fallback_used = False
        warnings: list[str] = []
        started = time.perf_counter()
        last_error: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                if not self.api_key and not self.base_url:
                    raise RuntimeError(f"No credentials configured for provider {self.provider}")
                payload, tokens = self._call_anthropic(user_prompt) if self.provider == "anthropic" else self._call_openai(user_prompt)
                break
            except Exception as exc:
                last_error = exc
                logger.warning("Extraction attempt %s failed: %s", attempt + 1, exc)
                if attempt < self.max_retries:
                    time.sleep(min(2 ** attempt, 4))
        if payload is None:
            if not self.enable_local_fallback:
                raise RuntimeError("LLM extraction failed") from last_error
            payload = self._simulate(document_text)
            fallback_used = True
            tokens = 0
            warnings.append(f"LLM failed; deterministic development fallback used: {str(last_error)[:160]}")
        entities, validation_warnings = self._post_validate(payload, document_text)
        warnings.extend(validation_warnings)
        return ExtractionResult(
            entities=entities, model_name=self.model_name, provider=self.provider,
            prompt_version=self.prompt_version, prompt_hash=self.prompt_hash,
            system_prompt_hash=self.system_prompt_hash, tokens_used=tokens,
            latency_ms=(time.perf_counter() - started) * 1000, document_id=document_id,
            document_metadata=meta, validation_warnings=warnings, fallback_used=fallback_used,
        )

    def extract_batch(self, docs: list[dict[str, Any]]) -> list[ExtractionResult]:
        return [self.extract(doc.get("text", ""), doc.get("id"), doc.get("metadata")) for doc in docs]


def enrich_evidence_with_llm_entities(evidence: Any, extractor: LLMEntityExtractor) -> Any:
    is_dict = isinstance(evidence, dict)
    getter = evidence.get if is_dict else lambda key, default=None: getattr(evidence, key, default)
    text = getter("text") or getter("content") or getter("document_text") or ""
    document_id = getter("id") or getter("document_id")
    metadata = getter("metadata") or getter("meta") or {}
    if len(text.strip()) < 20:
        logger.warning("Evidence %s has insufficient text; extraction skipped", document_id)
        return evidence
    if not isinstance(metadata, dict):
        metadata = dict(metadata)
    result = extractor.extract(text, document_id, metadata)
    provenance = result.model_dump(exclude={"entities"}) | {"summary": result.summary()}
    if is_dict:
        evidence["entities"] = list(evidence.get("entities") or []) + result.to_evidence_entities()
        evidence["extraction_metadata"] = provenance
        evidence["extraction_result"] = result.model_dump()
    else:
        setattr(evidence, "entities", list(getattr(evidence, "entities", None) or []) + result.to_evidence_entities())
        setattr(evidence, "extraction_metadata", provenance)
        setattr(evidence, "extraction_result", result)
    return evidence
