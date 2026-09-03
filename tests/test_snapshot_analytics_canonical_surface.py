from types import SimpleNamespace

from recording.snapshot_recorder import SnapshotRecorder
from simulation.replay_loader import ReplayLoader


CANONICAL_ANALYTICS_FIELDS = {
    "dealer",
    "dealer_flow",
    "liquidity",
    "gamma_flip",
    "gamma_wall",
    "oi_flow",
    "iv_skew",
    "iv_smile",
    "expected_move",
    "max_pain",
    "pcr",
    "market_structure",
    "atr",
    "volatility",
    "technical",
    "probability",
    "signal",
    "smart_strike",
    "trade_plan",
    "risk",
    "institutional_score",
    "market_map",
}


def test_canonical_analytics_surface_survives_snapshot_record_and_replay(tmp_path):
    analytics = {
        field_name: {"sentinel": field_name}
        for field_name in sorted(CANONICAL_ANALYTICS_FIELDS)
    }
    context = SimpleNamespace(
        timestamp="2026-09-03 09:30:00",
        cycle_no=1,
        symbol="NIFTY",
        spot=25000.0,
        expiry="2026-09-10",
        runtime_status="LIVE",
        regime="NEUTRAL",
        trade_status="WAIT",
        trade_block_reason=None,
        data_provenance=None,
        analytics=analytics,
        decision={"signal": "WAIT"},
        explanation={"reason": "canonical snapshot test"},
        intelligence={"recommendation": "WAIT"},
        option_chain=None,
        greeks_df=None,
    )

    recorder = SnapshotRecorder(root=tmp_path)
    assert recorder.save(context) is True

    replay = ReplayLoader().load(tmp_path / "2026-09-03" / "000001_09-30-00")

    assert set(replay.analytics) == CANONICAL_ANALYTICS_FIELDS
    assert replay.analytics == analytics
