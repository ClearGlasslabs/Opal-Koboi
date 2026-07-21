"""Defensive browser intelligence primitives for ClearGlassInc Artemis.

This module is intentionally local-first and public-source-only. It models tabs,
notes, captures, citations, encrypted secret envelopes, RBAC decisions, and audit
records for a lawful browser research assistant. It does not contain scanning,
credential collection, exploitation, deception, or unauthorized access behavior.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Iterable
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class BrowserRole(StrEnum):
    VIEWER = "viewer"
    RESEARCHER = "researcher"
    ADMIN = "admin"
    AUDITOR = "auditor"


class BrowserAction(StrEnum):
    READ = "read"
    WRITE_NOTE = "write_note"
    CAPTURE_SOURCE = "capture_source"
    MANAGE_SECRETS = "manage_secrets"
    VIEW_AUDIT = "view_audit"


ROLE_PERMISSIONS: dict[BrowserRole, set[BrowserAction]] = {
    BrowserRole.VIEWER: {BrowserAction.READ},
    BrowserRole.RESEARCHER: {BrowserAction.READ, BrowserAction.WRITE_NOTE, BrowserAction.CAPTURE_SOURCE},
    BrowserRole.ADMIN: set(BrowserAction),
    BrowserRole.AUDITOR: {BrowserAction.READ, BrowserAction.VIEW_AUDIT},
}


class SourceKind(StrEnum):
    PUBLIC_WEB = "public_web"
    PUBLIC_DATASET = "public_dataset"
    GOVERNMENT = "government"
    ACADEMIC = "academic"
    VENDOR_ADVISORY = "vendor_advisory"


class ResearchSource(StrictModel):
    url: HttpUrl
    title: str = Field(min_length=1, max_length=240)
    kind: SourceKind = SourceKind.PUBLIC_WEB
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    content_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    license_note: str = Field(default="Store metadata and short excerpts only; respect source terms.")

    @field_validator("url")
    @classmethod
    def public_sources_only(cls, value: HttpUrl) -> HttpUrl:
        parsed = urlparse(str(value))
        host = parsed.hostname or ""
        if parsed.scheme != "https":
            raise ValueError("sources must use https")
        if host in {"localhost", "127.0.0.1", "0.0.0.0"} or host.endswith(".local"):
            raise ValueError("local/private sources are not OSINT inputs")
        return value


class Citation(StrictModel):
    claim: str = Field(min_length=1)
    source_url: HttpUrl
    evidence_quote: str = Field(min_length=1, max_length=280)
    source_hash: str = Field(pattern=r"^[a-f0-9]{64}$")


class AISummary(StrictModel):
    summary: str = Field(min_length=1)
    citations: list[Citation] = Field(min_length=1)

    @model_validator(mode="after")
    def every_sentence_has_citation(self) -> "AISummary":
        claims = [s for s in re.split(r"(?<=[.!?])\s+", self.summary.strip()) if s]
        if len(self.citations) < len(claims):
            raise ValueError("every summary claim/sentence requires at least one citation")
        return self


class BrowserTab(StrictModel):
    tab_id: str = Field(min_length=1)
    url: HttpUrl
    title: str
    sources: list[ResearchSource] = Field(default_factory=list)


class ResearchNote(StrictModel):
    note_id: str
    body: str = Field(min_length=1, max_length=8000)
    source_urls: list[HttpUrl] = Field(default_factory=list)
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuditEvent(StrictModel):
    actor_id: str
    action: BrowserAction
    target: str
    allowed: bool
    reason: str
    at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_hash: str = ""

    def seal(self) -> "AuditEvent":
        payload = self.model_dump(mode="json", exclude={"event_hash"})
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        return self.model_copy(update={"event_hash": digest})


@dataclass(slots=True)
class LocalFirstVault:
    """Small encrypted-envelope helper using stdlib primitives for offline tests.

    Production deployments should back this interface with OS keychain, WebCrypto,
    KMS/HSM wrapped keys, or libsodium. The format authenticates ciphertext with
    HMAC-SHA256 and derives a stream key with PBKDF2-HMAC-SHA256.
    """

    passphrase: str
    iterations: int = 210_000

    def _key(self, salt: bytes) -> bytes:
        return hashlib.pbkdf2_hmac("sha256", self.passphrase.encode(), salt, self.iterations, dklen=32)

    def encrypt(self, secret: str) -> dict[str, str | int]:
        salt = os.urandom(16)
        nonce = os.urandom(16)
        key = self._key(salt)
        stream = hashlib.pbkdf2_hmac("sha256", key, nonce, 1, dklen=len(secret.encode()))
        ciphertext = bytes(a ^ b for a, b in zip(secret.encode(), stream, strict=True))
        mac = hmac.new(key, nonce + ciphertext, hashlib.sha256).hexdigest()
        return {
            "v": 1,
            "kdf": "pbkdf2-hmac-sha256",
            "iterations": self.iterations,
            "salt": base64.b64encode(salt).decode(),
            "nonce": base64.b64encode(nonce).decode(),
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "mac": mac,
        }

    def decrypt(self, envelope: dict[str, str | int]) -> str:
        salt = base64.b64decode(str(envelope["salt"]))
        nonce = base64.b64decode(str(envelope["nonce"]))
        ciphertext = base64.b64decode(str(envelope["ciphertext"]))
        key = self._key(salt)
        expected = hmac.new(key, nonce + ciphertext, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, str(envelope["mac"])):
            raise ValueError("secret envelope authentication failed")
        stream = hashlib.pbkdf2_hmac("sha256", key, nonce, 1, dklen=len(ciphertext))
        return bytes(a ^ b for a, b in zip(ciphertext, stream, strict=True)).decode()


def authorize_browser_action(role: BrowserRole, action: BrowserAction, actor_id: str, target: str) -> AuditEvent:
    allowed = action in ROLE_PERMISSIONS[role]
    reason = "role permission granted" if allowed else f"{role.value} cannot perform {action.value}"
    return AuditEvent(actor_id=actor_id, action=action, target=target, allowed=allowed, reason=reason).seal()


def source_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def build_cited_summary(claims: Iterable[tuple[str, ResearchSource, str]]) -> AISummary:
    sentences: list[str] = []
    citations: list[Citation] = []
    for claim, source, quote in claims:
        sentences.append(claim.rstrip(".") + ".")
        citations.append(Citation(claim=claim, source_url=source.url, evidence_quote=quote, source_hash=source.content_sha256))
    return AISummary(summary=" ".join(sentences), citations=citations)


def new_id(prefix: str) -> str:
    return f"{prefix}_{secrets.token_urlsafe(12)}"
