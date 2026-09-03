import ast
from dataclasses import fields
from pathlib import Path

from models.market_context import MarketContext


EXPECTED_ANALYTICS_CONTEXT_FIELDS = {
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


def test_market_context_declares_complete_current_analytics_surface():
    declared = {field.name for field in fields(MarketContext)}
    assert EXPECTED_ANALYTICS_CONTEXT_FIELDS <= declared


def test_pipeline_context_assignments_are_declared_on_market_context():
    pipeline_path = Path(__file__).parents[1] / "analytics" / "analytics_pipeline.py"
    tree = ast.parse(pipeline_path.read_text(encoding="utf-8"))

    assigned = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == "context"
            ):
                assigned.add(target.attr)

    declared = {field.name for field in fields(MarketContext)}
    assert assigned <= declared
    assert EXPECTED_ANALYTICS_CONTEXT_FIELDS <= assigned


def test_market_context_new_canonical_fields_have_stable_defaults():
    context = MarketContext()

    for field_name in EXPECTED_ANALYTICS_CONTEXT_FIELDS:
        value = getattr(context, field_name)
        assert value == {}, field_name
