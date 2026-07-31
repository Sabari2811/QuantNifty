from __future__ import annotations

from backtesting.signal_adapter import SignalAdapter
from backtesting.trading_pipeline import TradingPipeline
from controllers.replay_controller import ReplayController


class BacktestEngine:
    """
    QuantNifty Backtest Engine.

    Executes historical replay through the EXACT same
    execution pipeline used by live paper trading.

    Pipeline
    --------

        ReplayController
                │
                ▼
        RuntimeContext
                │
                ▼
        SignalAdapter
                │
                ▼
        TradingPipeline
                │
                ▼
        PaperBroker
                │
                ▼
        TradeJournal
                │
                ▼
        PerformanceEngine

    Responsibilities
    ----------------
    • Drive replay
    • Extract TradingDecision
    • Execute paper trades
    • Update open positions
    • Return completed statistics

    It deliberately contains NO trading logic.
    """

    def __init__(
        self,
        replay_controller: ReplayController,
    ):

        self.controller = replay_controller

        self.adapter = SignalAdapter()

        self.pipeline = TradingPipeline()

    # =====================================================
    # Backtest
    # =====================================================

    def run(self):

        print("\n========== BACKTEST START ==========\n")

        broker = self.pipeline.paper_broker

        while self.controller.has_next():

            #
            # Execute one replay cycle.
            #
            ctx = self.controller.next()

            if ctx is None:
                break

            #
            # Extract TradingDecision.
            #
            decision = self.adapter.from_context(ctx)

            #
            # Execute entry.
            #
            if decision is not None:

                self.pipeline.process(

                    decision=decision,

                    snapshot=ctx,

                )

            #
            # Update existing positions.
            #
            option_chain = getattr(

                ctx,

                "option_chain",

                None,

            )

            broker.update_positions(

                option_chain

            )

        print("\n========== BACKTEST COMPLETE ==========\n")

        return {

            "portfolio": broker.portfolio,

            "journal": broker.journal,

            "performance": broker.performance,

        }