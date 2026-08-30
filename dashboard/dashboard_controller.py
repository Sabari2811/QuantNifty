from config.settings import PROVIDER

from models.dashboard_data import DashboardData
from models.dealer_data import DealerData

from runtime.runtime_manager import RuntimeManager
from dashboard.intelligence_adapter import adapt_intelligence


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
        analytics = ctx.analytics or {}
        dealer_analytics = analytics.get("dealer", {})
        option_chain_integrity = None
        if ctx.option_chain is not None:
            option_chain_integrity = ctx.option_chain.attrs.get("quote_integrity")

        canonical_intelligence = ctx.intelligence

        return DashboardData(
            provider=PROVIDER,
            symbol=ctx.symbol,
            spot=ctx.spot,
            expiry=ctx.expiry,
            dealer=DealerData(
                dealer_gamma=dealer_analytics.get("dealer_gamma"),
                market_mode=dealer_analytics.get("market_mode"),
                support=dealer_analytics.get("support"),
                resistance=dealer_analytics.get("resistance"),
                gamma_flip=dealer_analytics.get("gamma_flip"),
                gamma_wall=dealer_analytics.get("gamma_wall"),
                expected_volatility=dealer_analytics.get("expected_volatility"),
                mean_reversion_probability=dealer_analytics.get(
                    "mean_reversion_probability"
                ),
                breakout_probability=dealer_analytics.get("breakout_probability"),
                total_gex=dealer_analytics.get("total_gex"),
            ),
            dealer_flow=analytics.get("dealer_flow", {}),
            expected_move=analytics.get("expected_move", {}),
            max_pain=analytics.get("max_pain", {}),
            pcr=analytics.get("pcr", {}),
            market_structure=analytics.get("market_structure", {}),
            liquidity=analytics.get("liquidity", {}),
            probability=analytics.get("probability", {}),
            signal=analytics.get("signal", {}),
            trade_plan=analytics.get("trade_plan", {}),
            risk=analytics.get("risk", {}),
            institutional_score=analytics.get("institutional_score", {}),
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
        )
