import asyncio
from datetime import datetime, timezone

import pytest
from pydantic import SecretStr

from agents.registry import AgentRecord, AgentRegistry, AgentStatus
from executive.event_bus import EventBus, EventEnvelope, EventType
from policy.engine import Decision, PolicyEngine, PolicyRequest


def active_agent() -> AgentRecord:
    return AgentRecord(
        agent_id="agt_orion", tenant_id="tenant-a", codename="ORION", role="triage",
        permissions=frozenset({"action:correlate"}), mission_scope=frozenset({"mission-1"}),
        memory_partition="mem://tenant-a/mission-1/orion", status=AgentStatus.ACTIVE,
        last_heartbeat=datetime.now(timezone.utc),
    )


def test_registry_is_tenant_isolated_and_attested() -> None:
    registry = AgentRegistry(SecretStr("k" * 32))
    record = active_agent()
    proof = registry.register(record)
    assert registry.resolve("tenant-a", "agt_orion").codename == "ORION"
    with pytest.raises(PermissionError):
        registry.resolve("tenant-b", "agt_orion")
    assert registry.heartbeat("tenant-a", "agt_orion", proof).revision == 2


def test_event_bus_dispatches_and_rejects_replay() -> None:
    bus = EventBus()
    received: list[str] = []

    async def handler(event: EventEnvelope) -> None:
        received.append(event.event_id)

    bus.subscribe(EventType.INTEL_OBSERVED, handler)
    event = EventEnvelope(event_type=EventType.INTEL_OBSERVED, tenant_id="tenant-a", mission_id="mission-1",
                          producer="agt_orion", trace_id="trace-123", payload={"indicator": "redacted"},
                          idempotency_key="idem-123")
    assert asyncio.run(bus.publish(event)) == 1
    with pytest.raises(ValueError, match="replayed"):
        asyncio.run(bus.publish(event))


def test_policy_fails_closed_sanitizes_and_escalates() -> None:
    engine = PolicyEngine()
    denied = engine.evaluate(PolicyRequest(tenant_id="t", actor_id="a", roles=frozenset(), permissions=frozenset(),
                                           mission_id="m", action="export", risk_score=1, output="token=secret"))
    assert denied.decision == Decision.DENY
    assert denied.sanitized_output == "token=[REDACTED]"
    escalated = engine.evaluate(PolicyRequest(tenant_id="t", actor_id="a", roles=frozenset({"operator"}),
                                              permissions=frozenset({"action:recommend"}), mission_id="m",
                                              action="recommend", risk_score=80))
    assert escalated.decision == Decision.REQUIRE_APPROVAL
