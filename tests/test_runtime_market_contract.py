from __future__ import annotations

from datetime import datetime

from core.runtime_context import RuntimeContext


def test_runtime_context_can_carry_authoritative_market_snapshot():
    ctx = RuntimeContext()

    snapshot = object()

    ctx.snapshot = snapshot

    assert ctx.snapshot is snapshot


def test_runtime_context_preserves_market_provenance_fields():
    ctx = RuntimeContext()

    timestamp = datetime(2026, 8, 21, 9, 25)

    ctx.timestamp = timestamp
    ctx.trading_day = "2026-08-21"
    ctx.session = "LIVE"
    ctx.spot = 24270.85
    ctx.future = 24295.40
    ctx.india_vix = 12.75

    assert ctx.timestamp == timestamp
    assert ctx.trading_day == "2026-08-21"
    assert ctx.session == "LIVE"
    assert ctx.spot == 24270.85
    assert ctx.future == 24295.40
    assert ctx.india_vix == 12.75


def test_runtime_context_keeps_market_snapshot_and_raw_market_data_distinct():
    ctx = RuntimeContext()

    snapshot = object()
    option_chain = object()
    greeks_df = object()
    analytics = object()

    ctx.snapshot = snapshot
    ctx.option_chain = option_chain
    ctx.greeks_df = greeks_df
    ctx.analytics = analytics

    assert ctx.snapshot is snapshot
    assert ctx.option_chain is option_chain
    assert ctx.greeks_df is greeks_df
    assert ctx.analytics is analytics

    assert ctx.snapshot is not ctx.option_chain
    assert ctx.snapshot is not ctx.greeks_df
    assert ctx.snapshot is not ctx.analytics


def test_runtime_context_does_not_create_market_dependencies():
    ctx = RuntimeContext()

    assert ctx.snapshot is None
    assert ctx.option_chain is None
    assert ctx.greeks_df is None

    # RuntimeContext intentionally initializes analytics
    # as an empty container rather than None.
    assert ctx.analytics == {}


def test_runtime_context_can_be_populated_once_and_reused():
    ctx = RuntimeContext()

    snapshot = object()

    ctx.snapshot = snapshot

    first_reference = ctx.snapshot
    second_reference = ctx.snapshot

    assert first_reference is snapshot
    assert second_reference is snapshot
    assert first_reference is second_reference