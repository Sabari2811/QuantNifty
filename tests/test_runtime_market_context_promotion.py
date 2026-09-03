import ast
from dataclasses import fields
from pathlib import Path

from models.market_context import MarketContext
from core.runtime_context import RuntimeContext


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

    assignments = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Attribute)
                and isinstance(target.value.value, ast.Name)
                and target.value.value.id == "self"
                and target.value.attr == "market_context"
            ):
                assignments.append(node)

    assert assignments
    assignment = assignments[0]
    assert isinstance(assignment.value, ast.Name)
    assert assignment.value.id == "computed_context"


def test_market_context_and_serialized_analytics_surface_have_same_keys():
    context = MarketContext()
    context_dict = {name: getattr(context, name) for name in EXPECTED_ANALYTICS_FIELDS}
    assert set(context_dict) == EXPECTED_ANALYTICS_FIELDS
