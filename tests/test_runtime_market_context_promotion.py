import ast
from dataclasses import fields
from pathlib import Path

from core.runtime_context import RuntimeContext
from models.market_context import MarketContext


EXPECTED_ANALYTICS_FIELDS = {
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


def test_runtime_context_has_typed_market_context():
    runtime_field = next(
        field for field in fields(RuntimeContext)
        if field.name == "market_context"
    )
    assert runtime_field.default_factory is MarketContext
    assert isinstance(RuntimeContext().market_context, MarketContext)


def test_live_engine_promotes_pipeline_context_before_analytics_projection():
    engine_path = Path(__file__).parents[1] / "engine" / "live_engine.py"
    tree = ast.parse(engine_path.read_text(encoding="utf-8"))

    market_context_assignments = []
    analytics_assignments = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Attribute):
                continue
            if (
                isinstance(target.value, ast.Attribute)
                and isinstance(target.value.value, ast.Name)
                and target.value.value.id == "self"
                and target.value.attr == "ctx"
                and target.attr == "market_context"
            ):
                market_context_assignments.append(node)
            if (
                isinstance(target.value, ast.Attribute)
                and isinstance(target.value.value, ast.Name)
                and target.value.value.id == "self"
                and target.value.attr == "ctx"
                and target.attr == "analytics"
            ):
                analytics_assignments.append(node)

    assert market_context_assignments
    assert analytics_assignments

    promotion = min(market_context_assignments, key=lambda node: node.lineno)
    projection = min(analytics_assignments, key=lambda node: node.lineno)

    assert isinstance(promotion.value, ast.Name)
    assert promotion.value.id == "computed_context"
    assert promotion.lineno < projection.lineno


def test_market_context_and_serialized_analytics_surface_have_same_keys():
    context = MarketContext()
    context_dict = {
        name: getattr(context, name) for name in EXPECTED_ANALYTICS_FIELDS
    }
    assert set(context_dict) == EXPECTED_ANALYTICS_FIELDS
