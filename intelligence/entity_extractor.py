"""ClearGlass Financial Influence Watchdog v2.2.

Auditable, provider-neutral entity extraction for Ontario and Canadian
public-governance records. Production defaults are fail-closed.
"""
from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import re
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Annotated, Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator

logger = logging.getLogger(__name__)
PROMPT_VERSION = "v2.2.0-governance-ca-2026-07-20"
MAX_DOCUMENT_CHARS = 12_000
DEFAULT_GROQ_BASE_URL = "https://api.groq.com/openai/v1"

SYSTEM_PROMPT = """You are a forensic entity extraction specialist for Canadian public-sector accountability.

MISSION: Extract only entities relevant to financial-influence detection in Ontario municipal and provincial governance.

FOCUS:
- elected officials and jurisdictionally relevant MPs/MPPs
- senior municipal or provincial staff
- lobbyists, bidders, developers, contractors, numbered companies, public bodies, and nonprofits
- contract values, campaign contributions, grants, fines, and budget amounts
- procurement identifiers, contract awards, decision dates, filing dates, deadlines, motions, statutes, bylaws, and regulations

NON-NEGOTIABLE RULES:
1. Every entity must be directly supported by the supplied document text.
2. Never infer a role, affiliation, relationship, amount, date, party, or jurisdiction.
3. context_snippet must be an exact 10-30 word quotation from the document.
4. confidence is 0.0-1.0 and reflects textual clarity, not importance.
5. Normalize financial amounts numerically while preserving amount_text and explicit currency.
6. Return each unique entity once.
7. Use null or false when the document does not establish a field.
8. Output only data matching the supplied schema; no commentary.
"""

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

Extract all influence-relevant entities."""


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ExtractedEntity(StrictModel):
    entity_type: str
    name: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    context_snippet: str = Field(min_length=1)
    start_char: Optional[int] = Field(default=None, ge=0)
    end_char: Optional[int] = Field(default=None, ge=0)
    extraction_notes: Optional[str] = None

    @field_validator("confidence")
    @classmethod
    def finite_confidence(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("confidence must be finite")
        return value


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
        "BIDDER",
        "DEVELOPER",
        "LOBBY_FIRM",
        "MUNICIPAL_DEPT",
        "PROVINCIAL_BODY",
        "NUMBERED_COMPANY",
        "NONPROFIT",
        "OTHER",
    ] = "OTHER"
    registration_number: Optional[str] = None
    is_numbered_company: bool = False


class FinancialAmountEntity(ExtractedEntity):
    entity_type: Literal["FINANCIAL_AMOUNT"] = "FINANCIAL_AMOUNT"
    amount: float = Field(ge=0)
    currency: str = Field(default="CAD", min_length=3, max_length=3)
    amount_text: str = Field(min_length=1)
    is_contract_value: bool = False
    is_campaign_contribution: bool = False
    context: Literal["CONTRACT", "BUDGET", "CONTRIBUTION", "FINE", "GRANT", "OTHER"] = "OTHER"

    @field_validator("amount")
    @classmethod
    def finite_amount(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("amount must be finite")
        return value

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()


class ContractEntity(ExtractedEntity):
    entity_type: Literal["CONTRACT"] = "CONTRACT"
    contract_id: Optional[str] = None
    title: Optional[str] = None
    vendor_name: Optional[str] = None
    buyer_name: Optional[str] = None
    value_amount: Optional[float] = Field(default=None, ge=0)


class DateEntity(ExtractedEntity):
    entity_type: Literal["DATE"] = "DATE"
    date_text: str = Field(min_length=1)
    iso_date: Optional[str] = None
    date_type: Literal[
        "DECISION_DATE", "MEETING_DATE", "AWARD_DATE", "FILING_DATE", "DEADLINE", "OTHER"
    ] = "OTHER"

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
            "municipal freedom of information": "Municipal Freedom of Information and Protection of Privacy Act",
            "lobbyists registration act": "Lobbyists Registration Act, 1998",
        }
        lower = value.casefold()
        return next((canonical for key, canonical in aliases.items() if key in lower), value)


AnyInfluenceEntity = Annotated[
    Union[
        PersonEntity,
        OrganizationEntity,
        FinancialAmountEntity,
        ContractEntity,
        DateEntity,
        PolicyEntity,
    ],
    Field(discriminator="entity_type"),
]
_ENTITY_ADAPTER = TypeAdapter(AnyInfluenceEntity)


class ExtractionPayload(StrictModel):
    entities: list[AnyInfluenceEntity] = Field(default_factory=list)


class ExtractionResult(StrictModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    entities: list[AnyInfluenceEntity]
    provider: str
    model_name: str
    prompt_version: str
    prompt_hash: str
    prompt_template_hash: str
    system_prompt_hash: str
    schema_hash: str
    document_sha256: str
    tokens_used: Optional[int] = None
    latency_ms: float = Field(ge=0)
    extraction_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    document_id: Optional[str] = None
    document_metadata: dict[str, Any] = Field(default_factory=dict)
    source_characters: int = Field(ge=0)
    submitted_characters: int = Field(ge=0)
    truncated: bool = False
    attempts: int = Field(ge=1)
    validation_warnings: list[str] = Field(default_factory=list)
    fallback_used: bool = False

    def to_evidence_entities(self) -> list[dict[str, Any]]:
        return [entity.model_dump(mode="json") for entity in self.entities]

    def summary(self) -> dict[str, int]:
        return dict(Counter(entity.entity_type for entity in self.entities))


class LLMEntityExtractor:
    """Provider-neutral, fail-closed entity extraction service."""

    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        provider: Literal["auto", "openai", "anthropic", "compatible"] = "auto",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        prompt_version: str = PROMPT_VERSION,
        temperature: float = 0.0,
        max_retries: int = 2,
        retry_backoff_seconds: float = 0.5,
        enable_local_fallback: bool = False,
        strict_grounding: bool = True,
    ) -> None:
        self.model_name = model_name
        self.provider = self._resolve_provider(provider, model_name, base_url)
        self.base_url = base_url or self._provider_base_url(self.provider)
        self.api_key = api_key or self._provider_key(self.provider)
        self.prompt_version = prompt_version
        self.temperature = temperature
        self.max_retries = max(0, max_retries)
        self.retry_backoff_seconds = max(0.0, retry_backoff_seconds)
        self.enable_local_fallback = enable_local_fallback
        self.strict_grounding = strict_grounding
        self.system_prompt_hash = self._hash(SYSTEM_PROMPT)
        self.prompt_template_hash = self._hash(USER_PROMPT)
        self.schema_hash = self._hash(self._canonical_json(ExtractionPayload.model_json_schema()))

    @staticmethod
    def _hash(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def _canonical_json(value: Any) -> str:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)

    @staticmethod
    def _resolve_provider(provider: str, model_name: str, base_url: Optional[str]) -> str:
        if provider != "auto":
            return provider
        if base_url:
            return "compatible"
        if "claude" in model_name.casefold():
            return "anthropic"
        if os.getenv("GROQ_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            return "compatible"
        return "openai"

    @staticmethod
    def _provider_key(provider: str) -> Optional[str]:
        if provider == "anthropic":
            return os.getenv("ANTHROPIC_API_KEY")
        if provider == "compatible":
            return os.getenv("OPENAI_COMPATIBLE_API_KEY") or os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
        return os.getenv("OPENAI_API_KEY")

    @staticmethod
    def _provider_base_url(provider: str) -> Optional[str]:
        if provider != "compatible":
            return None
        return os.getenv("OPENAI_COMPATIBLE_BASE_URL") or (
            DEFAULT_GROQ_BASE_URL if os.getenv("GROQ_API_KEY") else None
        )

    @staticmethod
    def _safe_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
        return json.loads(json.dumps(metadata, default=str))

    @staticmethod
    def _safe_error(exc: Exception) -> str:
        text = re.sub(r"(?i)(api[_-]?key|authorization)\s*[:=]\s*\S+", r"\1=[REDACTED]", str(exc))
        return f"{type(exc).__name__}: {text[:180]}"

    def _build_user_prompt(self, text: str, metadata: dict[str, Any]) -> tuple[str, int, bool]:
        clean = text.strip()
        truncated = len(clean) > MAX_DOCUMENT_CHARS
        if truncated:
            candidate = clean[:MAX_DOCUMENT_CHARS]
            clean = candidate.rsplit(" ", 1)[0] if " " in candidate else candidate
            clean += "\n...[TRUNCATED]"
        prompt = USER_PROMPT.format(
            title=metadata.get("title", "Untitled"),
            source_type=metadata.get("source_type", "unknown"),
            jurisdiction=metadata.get("jurisdiction", "Ontario"),
            retrieved_at=metadata.get("retrieved_at", datetime.now(timezone.utc).isoformat()),
            document_id=metadata.get("document_id", "unknown"),
            document_text=clean,
        )
        return prompt, len(clean), truncated

    def _call_openai(self, user_prompt: str) -> tuple[ExtractionPayload, Optional[int]]:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        completion = client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format=ExtractionPayload,
            temperature=self.temperature,
        )
        payload = completion.choices[0].message.parsed
        if payload is None:
            raise ValueError("OpenAI returned no parsed structured output")
        return payload, completion.usage.total_tokens if completion.usage else None

    def _call_compatible(self, user_prompt: str) -> tuple[ExtractionPayload, Optional[int]]:
        from openai import OpenAI

        if not self.base_url:
            raise RuntimeError("compatible provider requires base_url or OPENAI_COMPATIBLE_BASE_URL")
        client = OpenAI(api_key=self.api_key or "local-not-required", base_url=self.base_url)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT + "\nReturn one JSON object with key 'entities'."},
            {"role": "user", "content": user_prompt},
        ]
        try:
            completion = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=self.temperature,
            )
        except Exception as first_error:
            logger.info(
                "Compatible endpoint rejected JSON mode; retrying plain JSON request: %s",
                type(first_error).__name__,
            )
            completion = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
            )
        content = completion.choices[0].message.content or ""
        payload = ExtractionPayload.model_validate_json(self._extract_json_object(content))
        return payload, completion.usage.total_tokens if completion.usage else None

    def _call_anthropic(self, user_prompt: str) -> tuple[ExtractionPayload, Optional[int]]:
        import anthropic

        client = anthropic.Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model=self.model_name,
            max_tokens=4096,
            temperature=self.temperature,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
            tools=[{
                "name": "submit_extraction",
                "description": "Submit the grounded extraction payload.",
                "input_schema": ExtractionPayload.model_json_schema(),
            }],
            tool_choice={"type": "tool", "name": "submit_extraction"},
        )
        tool_blocks = [block for block in response.content if getattr(block, "type", "") == "tool_use"]
        if not tool_blocks:
            raise ValueError("Anthropic returned no submit_extraction tool call")
        payload = ExtractionPayload.model_validate(tool_blocks[0].input)
        usage = getattr(response, "usage", None)
        tokens = (usage.input_tokens + usage.output_tokens) if usage else None
        return payload, tokens

    @staticmethod
    def _extract_json_object(text: str) -> str:
        stripped = text.strip()
        if stripped.startswith("```"):
            stripped = re.sub(r"^```(?:json)?\s*|\s*```$", "", stripped, flags=re.IGNORECASE)
        start, end = stripped.find("{"), stripped.rfind("}")
        if start < 0 or end < start:
            raise ValueError("provider response did not contain a JSON object")
        return stripped[start : end + 1]

    def _simulate(self, text: str) -> ExtractionPayload:
        """Deterministic development fallback. Never enabled by default."""
        entities: list[AnyInfluenceEntity] = []
        for match in re.finditer(r"\$\s?([\d,]+(?:\.\d{1,2})?)\s*([MBK]?)\b", text, re.IGNORECASE):
            raw, suffix = match.group(0), match.group(2).upper()
            amount = float(match.group(1).replace(",", "")) * {
                "B": 1_000_000_000,
                "M": 1_000_000,
                "K": 1_000,
            }.get(suffix, 1)
            snippet = self._snippet(text, match.start(), match.end())
            entities.append(FinancialAmountEntity(
                name=raw,
                confidence=0.80,
                context_snippet=snippet,
                start_char=match.start(),
                end_char=match.end(),
                amount=amount,
                amount_text=raw,
                is_contract_value="contract" in snippet.casefold() or "award" in snippet.casefold(),
                context="CONTRACT" if "contract" in snippet.casefold() or "award" in snippet.casefold() else "OTHER",
            ))
        role_pattern = re.compile(
            r"\b(Mayor|Councillor|Councilor|CAO|City Manager|Clerk|Regional Chair|"
            r"Director of [A-Za-z &]+)\s+([A-Z][A-Za-z'’-]+(?:\s+[A-Z][A-Za-z'’-]+){1,3})"
        )
        for match in role_pattern.finditer(text):
            role, name = match.groups()
            lower = role.casefold()
            entities.append(PersonEntity(
                name=name,
                confidence=0.85,
                context_snippet=self._snippet(text, match.start(), match.end()),
                start_char=match.start(),
                end_char=match.end(),
                role=role,
                is_elected_official=any(term in lower for term in ("mayor", "councillor", "councilor")),
                is_senior_staff=any(term in lower for term in ("cao", "manager", "director", "clerk")),
            ))
        return ExtractionPayload(entities=entities)

    @staticmethod
    def _snippet(text: str, start: int, end: int, radius: int = 90) -> str:
        raw = text[max(0, start - radius) : min(len(text), end + radius)]
        return " ".join(raw.split())

    @staticmethod
    def _normalized_contains(source: str, snippet: str) -> bool:
        return " ".join(snippet.split()) in " ".join(source.split())

    def _post_validate(
        self,
        payload: ExtractionPayload,
        source_text: str,
    ) -> tuple[list[AnyInfluenceEntity], list[str]]:
        warnings: list[str] = []
        output: list[AnyInfluenceEntity] = []
        seen: set[tuple[str, str]] = set()
        source_casefold = source_text.casefold()

        for entity in payload.entities:
            key = (entity.entity_type, entity.name.casefold())
            if key in seen:
                warnings.append(f"Duplicate removed: {entity.entity_type}:{entity.name}")
                continue
            seen.add(key)

            snippet_grounded = entity.context_snippet in source_text or self._normalized_contains(
                source_text, entity.context_snippet
            )
            name_grounded = entity.name.casefold() in source_casefold
            if not snippet_grounded or not name_grounded:
                disposition = "dropped" if self.strict_grounding else "flagged"
                warnings.append(f"Ungrounded entity {disposition}: {entity.entity_type}:{entity.name}")
                if self.strict_grounding:
                    continue
                entity.confidence = min(entity.confidence, 0.5)

            word_count = len(entity.context_snippet.split())
            if not 10 <= word_count <= 30:
                warnings.append(
                    f"Context snippet outside 10-30 words ({word_count}): {entity.entity_type}:{entity.name}"
                )

            exact_start = source_text.find(entity.context_snippet)
            if exact_start >= 0:
                entity.start_char = exact_start
                entity.end_char = exact_start + len(entity.context_snippet)
            elif entity.start_char is not None and entity.end_char is not None:
                if entity.start_char > entity.end_char or entity.end_char > len(source_text):
                    warnings.append(f"Invalid offsets cleared: {entity.entity_type}:{entity.name}")
                    entity.start_char = entity.end_char = None

            if isinstance(entity, FinancialAmountEntity) and entity.amount > 10_000_000_000:
                warnings.append(f"Large amount requires analyst review: {entity.amount_text}")
                entity.confidence = min(entity.confidence, 0.6)

            if isinstance(entity, OrganizationEntity) and re.match(
                r"^\d{6,9}\s+(?:ONTARIO|CANADA)?\s*(?:INC|CORP|LTD|LIMITED)\.?$",
                entity.name.upper(),
            ):
                entity.is_numbered_company = True
                entity.org_type = "NUMBERED_COMPANY"

            if isinstance(entity, PersonEntity) and entity.role:
                role = entity.role.casefold()
                entity.is_elected_official = entity.is_elected_official or any(
                    term in role for term in ("mayor", "councillor", "councilor", "mpp", "mp")
                )
                entity.is_senior_staff = entity.is_senior_staff or any(
                    term in role for term in ("cao", "city manager", "director", "clerk", "chief")
                )
                entity.is_lobbyist = entity.is_lobbyist or "lobby" in role

            output.append(_ENTITY_ADAPTER.validate_python(entity))

        return output, warnings

    def _provider_call(self, user_prompt: str) -> tuple[ExtractionPayload, Optional[int]]:
        if self.provider == "anthropic":
            return self._call_anthropic(user_prompt)
        if self.provider == "compatible":
            return self._call_compatible(user_prompt)
        return self._call_openai(user_prompt)

    def extract(
        self,
        document_text: str,
        document_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> ExtractionResult:
        if len(document_text.strip()) < 20:
            raise ValueError("document_text must contain at least 20 non-whitespace characters")

        meta = self._safe_metadata(dict(metadata or {}))
        meta["document_id"] = document_id or meta.get("document_id", "unknown")
        meta.setdefault("title", meta["document_id"])
        meta.setdefault("source_type", "council_minutes")
        meta.setdefault("jurisdiction", "Ontario")

        user_prompt, submitted_characters, truncated = self._build_user_prompt(document_text, meta)
        actual_prompt_hash = self._hash(
            SYSTEM_PROMPT + user_prompt + self._canonical_json(ExtractionPayload.model_json_schema()) + self.prompt_version
        )
        document_hash = self._hash(document_text)

        payload: Optional[ExtractionPayload] = None
        tokens: Optional[int] = None
        fallback_used = False
        warnings: list[str] = []
        started = time.perf_counter()
        last_error: Optional[Exception] = None
        attempts = 0

        for attempt in range(self.max_retries + 1):
            attempts = attempt + 1
            try:
                if self.provider in {"openai", "anthropic"} and not self.api_key:
                    raise RuntimeError(f"No credentials configured for provider {self.provider}")
                if self.provider == "compatible" and not self.base_url:
                    raise RuntimeError("No compatible provider base URL configured")
                payload, tokens = self._provider_call(user_prompt)
                break
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Extraction attempt %s/%s failed: %s",
                    attempts,
                    self.max_retries + 1,
                    self._safe_error(exc),
                )
                if attempt < self.max_retries and self.retry_backoff_seconds:
                    time.sleep(min(self.retry_backoff_seconds * (2**attempt), 4.0))

        if payload is None:
            if not self.enable_local_fallback:
                detail = self._safe_error(last_error or RuntimeError("unknown error"))
                raise RuntimeError(f"LLM extraction failed after {attempts} attempt(s): {detail}") from last_error
            payload = self._simulate(document_text)
            fallback_used = True
            tokens = 0
            warnings.append(
                "LLM failed; deterministic development fallback used: "
                + self._safe_error(last_error or RuntimeError("unknown error"))
            )

        entities, validation_warnings = self._post_validate(payload, document_text)
        warnings.extend(validation_warnings)

        return ExtractionResult(
            entities=entities,
            provider=self.provider,
            model_name=self.model_name,
            prompt_version=self.prompt_version,
            prompt_hash=actual_prompt_hash,
            prompt_template_hash=self.prompt_template_hash,
            system_prompt_hash=self.system_prompt_hash,
            schema_hash=self.schema_hash,
            document_sha256=document_hash,
            tokens_used=tokens,
            latency_ms=(time.perf_counter() - started) * 1000,
            document_id=document_id,
            document_metadata=meta,
            source_characters=len(document_text),
            submitted_characters=submitted_characters,
            truncated=truncated,
            attempts=attempts,
            validation_warnings=warnings,
            fallback_used=fallback_used,
        )

    def extract_batch(
        self,
        docs: list[dict[str, Any]],
        max_workers: int = 4,
    ) -> list[ExtractionResult]:
        workers = max(1, min(max_workers, 32))

        def run(doc: dict[str, Any]) -> ExtractionResult:
            return self.extract(
                document_text=doc.get("text", ""),
                document_id=doc.get("id"),
                metadata=doc.get("metadata"),
            )

        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="clearglass-extract") as pool:
            return list(pool.map(run, docs))


def enrich_evidence_with_llm_entities(evidence: Any, extractor: LLMEntityExtractor) -> Any:
    """Enrich a dict-style or object-style Evidence record in place."""
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
    provenance = result.model_dump(mode="json", exclude={"entities"}) | {"summary": result.summary()}

    if is_dict:
        evidence["entities"] = list(evidence.get("entities") or []) + result.to_evidence_entities()
        evidence["extraction_metadata"] = provenance
        evidence["extraction_result"] = result.model_dump(mode="json")
    else:
        setattr(
            evidence,
            "entities",
            list(getattr(evidence, "entities", None) or []) + result.to_evidence_entities(),
        )
        setattr(evidence, "extraction_metadata", provenance)
        setattr(evidence, "extraction_result", result)
    return evidence
