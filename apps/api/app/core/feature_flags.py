"""Typed, fail-closed capability flags for high-risk integrations."""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType
from typing import Mapping


class Capability(StrEnum):
    AI = "ai"
    EMAIL = "email"
    BILLING = "billing"
    LIVE_DATA = "live_data"
    BLUE_TEAM = "blue_team"
    EXTERNAL_WEBHOOKS = "external_webhooks"


class FeatureFlags:
    """Immutable capability decisions; absent and malformed values are disabled."""

    def __init__(self, values: Mapping[Capability | str, bool] | None = None) -> None:
        supplied = values or {}
        self._values = MappingProxyType(
            {
                capability: supplied.get(capability, supplied.get(capability.value, False)) is True
                for capability in Capability
            }
        )

    def enabled(self, capability: Capability) -> bool:
        return self._values[capability]

    def snapshot(self) -> Mapping[Capability, bool]:
        return self._values


SAFE_DEFAULT_FLAGS = FeatureFlags()
