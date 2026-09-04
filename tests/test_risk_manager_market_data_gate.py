from types import SimpleNamespace

from risk.risk_manager import RiskManager


class FakeBroker:
    def __init__(self):
        self.portfolio = SimpleNamespace(
            open_positions=[],
            invested_amount=0,
            capital=500000,
        )


class FreshProvenance:
    spot = SimpleNamespace(
        freshness_verified=True,
        integrity_status="VALID",
    )
    option_chain = SimpleNamespace(
        freshness_verified=True,
        integrity_status="SUSPECT",
    )


class InvalidOptionChainProvenance:
    spot = SimpleNamespace(
        freshness_verified=True,
        integrity_status="VALID",
    )
    option_chain = SimpleNamespace(
        freshness_verified=True,
        integrity_status="INVALID",
    )


class StaleSpotProvenance:
    spot = SimpleNamespace(
        freshness_verified=False,
        integrity_status="VALID",
    )
    option_chain = SimpleNamespace(
        freshness_verified=True,
        integrity_status="VALID",
    )


def test_market_data_gate_accepts_fresh_suspect_chain_for_execution_policy():
    manager = RiskManager()
    ok, reason = manager._market_data_readiness(
        SimpleNamespace(data_provenance=FreshProvenance())
    )

    assert ok is True
    assert reason == ""


def test_market_data_gate_blocks_invalid_option_chain():
    manager = RiskManager()
    ok, reason = manager._market_data_readiness(
        SimpleNamespace(data_provenance=InvalidOptionChainProvenance())
    )

    assert ok is False
    assert reason == "option_chain Market Data Invalid"


def test_market_data_gate_blocks_unverified_spot_freshness():
    manager = RiskManager()
    ok, reason = manager._market_data_readiness(
        SimpleNamespace(data_provenance=StaleSpotProvenance())
    )

    assert ok is False
    assert reason == "spot Market Data Not Fresh"


def test_legacy_risk_manager_call_without_context_remains_compatible():
    manager = RiskManager()
    broker = FakeBroker()

    ok, reason = manager.validate(broker, None)

    assert ok is False
    assert reason == "Outside Market Hours"
