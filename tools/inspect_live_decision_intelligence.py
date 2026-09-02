from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.dashboard_controller import DashboardController
from dashboard.decision_adapter import adapt_decision
from dashboard.intelligence_adapter import adapt_intelligence
from dashboard.live_provider_reconciliation import compare_decision_intelligence_runtime


def _family_payload(item):
    return {
        "family": item.family,
        "direction": item.direction,
        "strength": item.strength,
        "confidence": item.confidence,
        "freshness": item.freshness,
        "bullish_score": item.bullish_score,
        "bearish_score": item.bearish_score,
        "conflict_score": item.conflict_score,
        "evidence_count": item.evidence_count,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect fresh live Decision/Intelligence semantics and evidence.")
    parser.add_argument("--symbol", default="NIFTY")
    parser.add_argument("--levels", type=int, default=5)
    args = parser.parse_args()

    controller = DashboardController()
    dashboard = controller.load(args.symbol, args.levels)
    ctx = controller.runtime.get_context()

    consistency = compare_decision_intelligence_runtime(ctx)
    intelligence = getattr(ctx, "intelligence", None)
    evidence_items = getattr(intelligence, "evidence_items", ()) if intelligence else ()

    report = {
        "cycle_no": ctx.cycle_no,
        "decision": adapt_decision(dashboard),
        "intelligence": adapt_intelligence(intelligence),
        "consistency": consistency,
        "evidence_items": [
            {
                "source_family": item.source_family,
                "feature": item.feature,
                "direction": item.direction,
                "strength": item.strength,
                "confidence": item.confidence,
                "freshness": item.freshness,
                "independence": item.independence,
                "reason": item.reason,
            }
            for item in evidence_items
        ],
        "evidence_summary": {
            "bullish_count": getattr(intelligence.evidence_summary, "bullish_count", 0) if intelligence else 0,
            "bearish_count": getattr(intelligence.evidence_summary, "bearish_count", 0) if intelligence else 0,
            "neutral_count": getattr(intelligence.evidence_summary, "neutral_count", 0) if intelligence else 0,
            "confluence_score": getattr(intelligence.evidence_summary, "confluence_score", 0.0) if intelligence else 0.0,
            "conflict_score": getattr(intelligence.evidence_summary, "conflict_score", 0.0) if intelligence else 0.0,
        },
    }

    print(json.dumps(report, indent=2, default=str))
    print(f"LIVE_DECISION_INTELLIGENCE_STATUS={consistency.get('status')}")
    print(f"LIVE_DECISION_INTELLIGENCE_SEMANTIC={consistency.get('semantic_status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
