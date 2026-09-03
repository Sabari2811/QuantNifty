from dataclasses import fields

from models.market_context import MarketContext


# Every analytics field produced by AnalyticsPipeline.run() has one explicit
# downstream dashboard disposition. Fields not promoted to dedicated
# DashboardData attributes remain available through the generic serialized
# analytics projection; they must not be recomputed by the UI.
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
    "oi_shift",
    "probability",
    "signal",
    "smart_strike",
    "trade_plan",
    "risk",
    "institutional_score",
    "market_map",
}

DEDICATED_DASHBOARD_FIELDS = {
    "dealer",
    "dealer_flow",
    "liquidity",
    "expected_move",
    "max_pain",
    "pcr",
    "market_structure",
    "probability",
    "signal",
    "trade_plan",
    "risk",
    "institutional_score",
}

REPRESENTED_BY_EXISTING_CANONICAL_MAPPING = {
    "gamma_flip",
    "gamma_wall",
    "smart_strike",
}

GENERIC_ANALYTICS_ONLY_FIELDS = {
    "oi_flow",
    "iv_skew",
    "iv_smile",
    "atr",
    "volatility",
    "technical",
    "oi_shift",
    "market_map",
}


def test_every_canonical_analytics_field_has_one_disposition():
    dispositions = (
        DEDICATED_DASHBOARD_FIELDS
        | REPRESENTED_BY_EXISTING_CANONICAL_MAPPING
        | GENERIC_ANALYTICS_ONLY_FIELDS
    )

    assert dispositions == CANONICAL_ANALYTICS_FIELDS
    assert not (
        DEDICATED_DASHBOARD_FIELDS & REPRESENTED_BY_EXISTING_CANONICAL_MAPPING
    )
    assert not (
        DEDICATED_DASHBOARD_FIELDS & GENERIC_ANALYTICS_ONLY_FIELDS
    )
    assert not (
        REPRESENTED_BY_EXISTING_CANONICAL_MAPPING & GENERIC_ANALYTICS_ONLY_FIELDS
    )


def test_disposition_matches_typed_market_context_analytics_surface():
    typed_fields = {
        item.name
        for item in fields(MarketContext)
        if item.name in CANONICAL_ANALYTICS_FIELDS
    }

    assert typed_fields == CANONICAL_ANALYTICS_FIELDS
