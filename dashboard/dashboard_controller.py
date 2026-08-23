from config.settings import PROVIDER

from models.dashboard_data import DashboardData
from models.dealer_data import DealerData

from dashboard.services.market_service import MarketService
from runtime.runtime_manager import RuntimeManager

from dashboard.intelligence_adapter import (
    adapt_intelligence,
    )


class DashboardController:

    def __init__(self):

        self.market = MarketService()

        # Shared Runtime (Singleton)
        self.runtime = RuntimeManager()

    # ======================================================
    # Load Dashboard
    # ======================================================

    def load(
        self,
        symbol,
        levels
    ):

        data = self.market.get_dashboard_data(
            symbol,
            levels
        )

        analytics = data["analytics"]

        # ==================================================
        # Dealer
        # ==================================================

        dealer = DealerData(

            dealer_gamma=analytics["dealer"]["dealer_gamma"],

            market_mode=analytics["dealer"]["market_mode"],

            support=analytics["dealer"]["support"],

            resistance=analytics["dealer"]["resistance"],

            gamma_flip=analytics["dealer"]["gamma_flip"],

            gamma_wall=analytics["dealer"]["gamma_wall"],

            expected_volatility=analytics["dealer"]["expected_volatility"],

            mean_reversion_probability=analytics["dealer"]["mean_reversion_probability"],

            breakout_probability=analytics["dealer"]["breakout_probability"],

            total_gex=analytics["dealer"]["total_gex"]

        )

        # ==================================================
        # Runtime Context
        # ==================================================

        ctx = self.runtime.get_context()

        # ==================================================
        # Dashboard
        # ==================================================

        dashboard = DashboardData(

            provider=PROVIDER,

            symbol=symbol,

            spot=data["spot"],

            expiry=data["expiry"],

            dealer=dealer,

            dealer_flow=analytics["dealer_flow"],

            expected_move=analytics["expected_move"],

            max_pain=analytics["max_pain"],

            pcr=analytics["pcr"],

            market_structure=analytics["market_structure"],

            liquidity=analytics["liquidity"],

            probability=analytics["probability"],

            signal=analytics["signal"],

            trade_plan=analytics["trade_plan"],

            risk=analytics["risk"],

            analytics=analytics,

            intelligence=adapt_intelligence(
                ctx.intelligence
            ),

            option_chain=data["option_chain"],

            institutional_score=analytics["institutional_score"],

            greeks=data["greeks"],

            # ==================================================
            # Runtime
            # ==================================================

            portfolio=ctx.portfolio,

            position=ctx.position,

            last_trade=ctx.last_trade,

            journal=ctx.journal,

            statistics=ctx.statistics,

            risk_state=ctx.risk_state,

            trade_status=ctx.trade_status,

            trade_block_reason=ctx.trade_block_reason,

            runtime_status=ctx.runtime_status,

            cycle_no=ctx.cycle_no

        )

        return dashboard