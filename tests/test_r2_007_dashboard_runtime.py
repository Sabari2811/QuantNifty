import pandas as pd

import dashboard.dashboard_controller as controller_module
from core.runtime_context import RuntimeContext


class FakeRuntime:
    def __init__(self):
        self.calls = []
        self.ctx = RuntimeContext()

    def run_once(self, symbol=None, levels=None):
        self.calls.append((symbol, levels))
        self.ctx.symbol = symbol
        self.ctx.strike_levels = levels
        self.ctx.spot = 25000.0
        self.ctx.expiry = "2026-08-27"
        self.ctx.option_chain = pd.DataFrame({"Strike": [25000]})
        self.ctx.greeks_df = pd.DataFrame({"Strike": [25000]})
        self.ctx.analytics = {
            "dealer": {},
            "dealer_flow": {},
            "expected_move": {},
            "max_pain": {},
            "pcr": {},
            "market_structure": {},
            "liquidity": {},
            "probability": {},
            "signal": {},
            "trade_plan": {},
            "risk": {},
            "institutional_score": {},
        }
        return self.ctx


def test_dashboard_controller_uses_canonical_runtime(monkeypatch):
    runtime = FakeRuntime()
    monkeypatch.setattr(
        controller_module,
        "RuntimeManager",
        lambda: runtime,
    )

    dashboard = controller_module.DashboardController().load(
        "BANKNIFTY",
        7,
    )

    assert runtime.calls == [("BANKNIFTY", 7)]
    assert dashboard.symbol == "BANKNIFTY"
    assert dashboard.spot == 25000.0
    assert dashboard.option_chain is runtime.ctx.option_chain
    assert dashboard.greeks is runtime.ctx.greeks_df


def test_runtime_context_preserves_dashboard_strike_selection():
    ctx = RuntimeContext()
    assert ctx.symbol == "NIFTY"
    assert ctx.strike_levels == 5
