from copy import deepcopy

from config.settings import PROVIDER

from models.dashboard_data import DashboardData
from models.dealer_data import DealerData

from runtime.runtime_manager import RuntimeManager
from dashboard.intelligence_adapter import adapt_intelligence
from dashboard.decision_intelligence_status import build_decision_intelligence_status


_WAIT_ACTIVE_FIELDS = (
    "recommended_strike",
    "option_type",
    "strike_score",
    "delta",
    "iv",
    "gex",
    "entry",
    "stop_loss",
    "target1",
    "target2",
    "risk_reward",
)

_TERMINAL_NON_EXECUTION = {"REJECTED", "FAILED", "NOT_SUBMITTED"}


def _effective_signal(ctx):
    """Return the executable signal after execution preparation/validation.

    A raw Decision may be BUY/SELL while the canonical execution gate rejects
    it (for example because Intelligence or decision/intelligence consistency
    vetoed the action). In that state the dashboard must expose WAIT as the
    executable state and must not display a stale actionable trade plan.
    """
    execution_result = getattr(ctx, "execution_result", None)
    execution_status = str(getattr(getattr(execution_result, "status", None), "value", "") or "").upper()
    if execution_status in _TERMINAL_NON_EXECUTION:
        return "WAIT"

    decision = getattr(ctx, "decision", None)
    signal = getattr(getattr(decision, "signal", None), "name", None)
    if signal:
        return str(signal).upper()
    canonical = getattr(ctx, "market_context", None)
    payload = getattr(canonical, "signal", {}) if canonical is not None else {}
    return str(payload.get("signal", "WAIT") or "WAIT").upper()


def _project_trade_plan(ctx):
    """Project a trade plan that cannot contradict executable decision state."""
    canonical = getattr(ctx, "market_context", None)
    source = getattr(canonical, "trade_plan", None) if canonical is not None else None
    plan = deepcopy(source or {})
    signal = _effective_signal(ctx)
    plan["signal"] = signal

    # ExecutionEngine can veto a market direction when the contract or
    # validation is invalid. In that state all executable fields must be
    # inactive in the UI. Keep analytical context such as ATR/volatility and
    # reasons, but never leave a stale strike/entry/target behind.
    if signal == "WAIT":
        for field in _WAIT_ACTIVE_FIELDS:
            if field in plan:
                plan[field] = None
        plan["option_type"] = ""
        plan["reasons"] = list(plan.get("reasons") or [])

    return plan


def _project_signal(ctx):
    """Project the exact executable signal/confidence into DashboardData."""
    decision = getattr(ctx, "decision", None)
    if decision is None:
        return {"signal": "WAIT", "confidence": 0.0, "reasons": []}
    signal = _effective_signal(ctx)
    confidence = getattr(getattr(decision, "signal", None), "confidence", 0.0)
    if signal == "WAIT":
        confidence = 0.0
    return {
        "signal": signal,
        "confidence": confidence,
        "reasons": list(getattr(decision, "reasons", []) or []),
    }


class DashboardController:
    """Build DashboardData exclusively from the canonical runtime context."""

    def __init__(self):
        self.runtime = RuntimeManager()

    def load(self, symbol, levels):
        """Load dashboard data from one canonical runtime cycle."""
        ctx = self.runtime.run_once(
            symbol=symbol,
            levels=levels,
        )
        canonical = ctx.market_context
        analytics = ctx.analytics or {}
        option_chain_integrity = None
        if ctx.option_chain is not None:
            option_chain_integrity = ctx.option_chain.attrs.get("quote_integrity")

        canonical_intelligence = ctx.intelligence
        decision_intelligence_consistency = None
        if ctx.decision is not None and canonical_intelligence is not None:
            decision_intelligence_consistency = build_decision_intelligence_status(
                ctx.decision,
                canonical_intelligence,
            )

        # Dashboard action state is deliberately projected from the post-
        # validation Decision, while analytics remain sourced from the typed
        # canonical MarketContext. This prevents a stale analytical direction
        # from appearing as an executable trade.
        dashboard_signal = _project_signal(ctx)
        dashboard_trade_plan = _project_trade_plan(ctx)

        return DashboardData(
            provider=PROVIDER,
            symbol=ctx.symbol,
            spot=ctx.spot,
            expiry=ctx.expiry,
            dealer=DealerData(
                dealer_gamma=canonical.dealer.get("dealer_gamma"),
                market_mode=canonical.dealer.get("market_mode"),
                support=canonical.dealer.get("support"),
                resistance=canonical.dealer.get("resistance"),
                gamma_flip=canonical.dealer.get("gamma_flip"),
                gamma_wall=canonical.dealer.get("gamma_wall"),
                expected_volatility=canonical.dealer.get("expected_volatility"),
                mean_reversion_probability=canonical.dealer.get(
                    "mean_reversion_probability"
                ),
                breakout_probability=canonical.dealer.get("breakout_probability"),
                total_gex=canonical.dealer.get("total_gex"),
            ),
            dealer_flow=canonical.dealer_flow,
            expected_move=canonical.expected_move,
            max_pain=canonical.max_pain,
            pcr=canonical.pcr,
            market_structure=canonical.market_structure,
            liquidity=canonical.liquidity,
            probability=canonical.probability,
            signal=dashboard_signal,
            trade_plan=dashboard_trade_plan,
            risk=canonical.risk,
            institutional_score=canonical.institutional_score,
            analytics=analytics,
            intelligence=adapt_intelligence(canonical_intelligence),
            canonical_intelligence=canonical_intelligence,
            option_chain=ctx.option_chain,
            greeks=ctx.greeks_df,
            data_provenance=ctx.data_provenance,
            option_chain_integrity=option_chain_integrity,
            execution_intent=ctx.execution_intent,
            execution_result=ctx.execution_result,
            execution_lifecycle=ctx.execution_lifecycle,
            position_recovery=ctx.position_recovery,
            position_reconciliation=ctx.position_reconciliation,
            portfolio=ctx.portfolio,
            position=ctx.position,
            last_trade=ctx.last_trade,
            journal=ctx.journal,
            statistics=getattr(ctx, "statistics", {}),
            risk_state=ctx.risk_state,
            brain_observation=getattr(ctx, "brain_observation", None),
            trade_status=ctx.trade_status,
            trade_block_reason=ctx.trade_block_reason,
            runtime_status=ctx.runtime_status,
            cycle_no=ctx.cycle_no,
            decision_intelligence_consistency=decision_intelligence_consistency,
        )
