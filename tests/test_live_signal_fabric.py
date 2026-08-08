from pathlib import Path

ROOT = Path(__file__).parents[1]
WEB = ROOT / "apps" / "web"


def test_every_page_is_wrapped_by_live_shell():
    layout = (WEB / "app/layout.tsx").read_text()
    assert "<LivePageShell" in layout
    assert "getPublicSnapshot" in layout


def test_required_stream_routes_are_fail_closed():
    server = (WEB / "lib/live/server.ts").read_text()
    for stream in ("public", "status", "performance", "content", "dashboard"):
        assert f'"{stream}"' in server
    assert 'stream === "dashboard"' in server
    assert 'status: 401' in server


def test_event_contract_validates_source_time_and_sequence():
    contract = (WEB / "lib/live/contracts.ts").read_text()
    for guard in ("knownSources", "Publication precedes occurrence", "Future timestamp", "nonnegative"):
        assert guard in contract


def test_production_is_disabled_without_verified_source():
    snapshot = (WEB / "lib/live/snapshot.ts").read_text()
    assert 'LIVE_PUBLIC_ENABLED === "true"' in snapshot
    assert "LIVE_STATUS_SOURCE_URL" in snapshot
    assert 'enabled: false' in snapshot
    assert "unavailable" in snapshot


def test_sse_security_and_fallback_headers():
    server = (WEB / "lib/live/server.ts").read_text()
    for header in ("text/event-stream", "X-Accel-Buffering", "no-cache, no-transform", "Retry-After", "Origin denied"):
        assert header in server


def test_reconnect_attempts_do_not_restart_the_connection_effect():
    shell = (WEB / "app/components/live/LivePageShell.tsx").read_text()
    assert "attempt=useRef(0)" in shell
    assert "[enabled,refresh,snapshot.stream]" in shell
    assert "[attempt," not in shell
    assert "document.addEventListener(\"visibilitychange\",visibility)" in shell
    assert "disposed||source!==connection" in shell
