"""Server-side protected-asset grants and non-invasive watermark descriptors."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from base64 import urlsafe_b64decode, urlsafe_b64encode
from dataclasses import dataclass


def _b64(value: bytes) -> str:
    return urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _unb64(value: str) -> bytes:
    return urlsafe_b64decode(value + "=" * (-len(value) % 4))


@dataclass(frozen=True)
class AssetGrant:
    asset_id: str
    account_id: str
    tier: str
    expires_at: int


class ProtectedAssetSigner:
    """Issue audience-specific, short-lived grants; key material stays server-side."""

    def __init__(self, secret: bytes, *, max_ttl_seconds: int = 900) -> None:
        if len(secret) < 32:
            raise ValueError("signing secret must contain at least 32 bytes")
        self._secret = secret
        self._max_ttl = max_ttl_seconds

    def issue(
        self, *, asset_id: str, account_id: str, tier: str, ttl_seconds: int = 300, now: int | None = None
    ) -> str:
        if not 1 <= ttl_seconds <= self._max_ttl:
            raise ValueError("ttl_seconds exceeds policy")
        issued = int(time.time() if now is None else now)
        payload = {"a": asset_id, "sub": account_id, "tier": tier, "exp": issued + ttl_seconds, "v": 1}
        encoded = _b64(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())
        signature = _b64(hmac.new(self._secret, encoded.encode(), hashlib.sha256).digest())
        return f"{encoded}.{signature}"

    def verify(self, token: str, *, expected_account_id: str, now: int | None = None) -> AssetGrant:
        try:
            encoded, supplied = token.split(".", 1)
            expected = hmac.new(self._secret, encoded.encode(), hashlib.sha256).digest()
            if not hmac.compare_digest(_unb64(supplied), expected):
                raise ValueError("invalid grant")
            payload = json.loads(_unb64(encoded))
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid grant") from exc
        current = int(time.time() if now is None else now)
        if payload.get("sub") != expected_account_id or current >= int(payload.get("exp", 0)):
            raise ValueError("expired or wrong grant audience")
        return AssetGrant(payload["a"], payload["sub"], payload["tier"], payload["exp"])


def watermark_label(grant: AssetGrant, *, rendered_at: int | None = None) -> str:
    """Return a subtle per-user label for server-side image/PDF rendering."""
    timestamp = int(time.time() if rendered_at is None else rendered_at)
    account_tag = hashlib.sha256(grant.account_id.encode()).hexdigest()[:12]
    return f"ClearGlassInc Artemis · account {account_tag} · {timestamp}"
