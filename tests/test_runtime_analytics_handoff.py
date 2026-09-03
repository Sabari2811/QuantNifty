import ast
from dataclasses import fields
from pathlib import Path

from models.market_context import MarketContext


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


ROOT = Path(__file__).resolve().parents[1]
PIPELINE_SOURCE = ROOT / "analytics" / "analytics_pipeline.py"
LIVE_ENGINE_SOURCE = ROOT / "engine" / "live_engine.py"


def _attribute_assignments(tree):
    return {
        node.targets[0].attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Attribute)
        and isinstance(node.targets[0].value, ast.Name)
        and node.targets[0].value.id == "context"
    }


def _return_dict_keys(tree):
    keys = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Return):
            continue
        if not isinstance(node.value, ast.Dict):
            continue
        for key in node.value.keys:
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                keys.add(key.value)
    return keys


def test_pipeline_context_and_return_share_complete_canonical_analytics_surface():
    tree = ast.parse(PIPELINE_SOURCE.read_text(encoding="utf-8"))
    context_assignments = _attribute_assignments(tree)
    return_keys = _return_dict_keys(tree)
    declared = {field.name for field in fields(MarketContext)}

    assert CANONICAL_ANALYTICS_FIELDS <= declared
    assert CANONICAL_ANALYTICS_FIELDS <= context_assignments
    assert CANONICAL_ANALYTICS_FIELDS <= return_keys


def test_live_engine_preserves_pipeline_result_as_runtime_analytics():
    tree = ast.parse(LIVE_ENGINE_SOURCE.read_text(encoding="utf-8"))

    matches = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        value = node.value
        if not (
            isinstance(target, ast.Attribute)
            and target.attr == "analytics"
            and isinstance(value, ast.Name)
            and value.id == "computed_analytics"
        ):
            continue

        owner = target.value
        if (
            isinstance(owner, ast.Attribute)
            and owner.attr == "ctx"
            and isinstance(owner.value, ast.Name)
            and owner.value.id == "self"
        ):
            matches.append(node)

    assert matches, "LiveEngine must preserve the AnalyticsPipeline result as ctx.analytics"
