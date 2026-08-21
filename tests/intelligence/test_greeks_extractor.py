from types import SimpleNamespace

import pandas as pd

from analytics.intelligence.extractors.greeks import GreeksExtractor
from analytics.intelligence.models import TradeIntelligenceRecord


def make_context(option_type="CE"):
    row = {
        "Strike": 25000,

        "CE_IV": 15.5,
        "CE_DELTA": 0.52,
        "CE_GAMMA": 0.012,
        "CE_THETA": -8.5,
        "CE_VEGA": 11.2,
        "CE_RHO": 1.4,
        "CE_OI": 125000,
        "CE_OI_CHANGE": 15000,
        "CE_VOLUME": 65000,

        "PE_IV": 16.2,
        "PE_DELTA": -0.48,
        "PE_GAMMA": 0.011,
        "PE_THETA": -7.8,
        "PE_VEGA": 10.7,
        "PE_RHO": -1.3,
        "PE_OI": 110000,
        "PE_OI_CHANGE": -9000,
        "PE_VOLUME": 58000,
    }

    return SimpleNamespace(
        greeks_df=pd.DataFrame([row]),
        decision=SimpleNamespace(
            trade=SimpleNamespace(
                strike=25000,
                option_type=option_type,
            )
        ),
    )


def test_extracts_call_greeks():
    ctx = make_context("CE")
    record = TradeIntelligenceRecord()

    GreeksExtractor().extract(ctx, record)

    assert record.strike == 25000
    assert record.option_type == "CE"
    assert record.implied_volatility == 15.5
    assert record.delta == 0.52
    assert record.gamma == 0.012
    assert record.theta == -8.5
    assert record.vega == 11.2
    assert record.rho == 1.4
    assert record.open_interest == 125000
    assert record.change_in_oi == 15000
    assert record.volume == 65000


def test_extracts_put_greeks():
    ctx = make_context("PE")
    record = TradeIntelligenceRecord()

    GreeksExtractor().extract(ctx, record)

    assert record.strike == 25000
    assert record.option_type == "PE"
    assert record.implied_volatility == 16.2
    assert record.delta == -0.48
    assert record.gamma == 0.011
    assert record.theta == -7.8
    assert record.vega == 10.7
    assert record.rho == -1.3
    assert record.open_interest == 110000
    assert record.change_in_oi == -9000
    assert record.volume == 58000


def test_missing_greeks_data_is_safe():
    ctx = SimpleNamespace(
        greeks_df=None,
        decision=None,
    )

    record = TradeIntelligenceRecord()

    GreeksExtractor().extract(ctx, record)

    assert record.delta == 0.0
    assert record.gamma == 0.0
    assert record.volume == 0.0


def test_invalid_option_type_is_safe():
    ctx = make_context("INVALID")
    record = TradeIntelligenceRecord()

    GreeksExtractor().extract(ctx, record)

    assert record.delta == 0.0
    assert record.gamma == 0.0
    assert record.option_type == ""


def test_missing_strike_is_safe():
    ctx = SimpleNamespace(
        greeks_df=pd.DataFrame(
            [{"Strike": 25000}]
        ),
        decision=SimpleNamespace(
            trade=SimpleNamespace(
                strike=None,
                option_type="CE",
            )
        ),
    )

    record = TradeIntelligenceRecord()

    GreeksExtractor().extract(ctx, record)

    assert record.delta == 0.0
