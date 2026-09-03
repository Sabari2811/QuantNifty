from config.settings import PROVIDER

from models.dashboard_data import DashboardData
from models.dealer_data import DealerData

from runtime.runtime_manager import RuntimeManager
from dashboard.intelligence_adapter import adapt_intelligence
from dashboard.decision_intelligence_status import build_decision_intelligence_status


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
            signal=canonical.signal,
            trade_plan=canonical.trade_plan,
            risk=canonical.risk,
            institutional_score=canonical.institutional_score,
            # Retain the established dictionary projection for generic analytics
            # display and snapshot compatibility. Dedicated DashboardData fields
            # above are sourced from the typed canonical MarketContext.
            analytics=analytics,
            intelligence=adapt_intelligence(canonical_intelligence),
            canonical_intelligence=canonical_intelligence,
            option_chain=ctx.option_chain,
            greeks=ctx.greeks_df,
            data_provenance=ctx.data_provenance,
            option_chain_integrity=option_chain_integrity,
            portfolio=ctx.portfolio,
            position=ctx.position,
            last_trade=ctx.last_trade,
            journal=ctx.journal,
            statistics=getattr(ctx, "statistics", {}),
            risk_state=ctx.risk_state,
            trade_status=ctx.trade_status,
            trade_block_reason=ctx.trade_block_reason,
            runtime_status=ctx.runtime_status,
            cycle_no=ctx.cycle_no,
            decision_intelligence_consistency=decision_intelligence_consistency,
        )
