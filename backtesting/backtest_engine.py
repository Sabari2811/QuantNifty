from __future__ import annotations

from backtesting.signal_adapter import SignalAdapter
from backtesting.trading_pipeline import TradingPipeline
from controllers.replay_controller import ReplayController


class BacktestEngine:
    """Run historical replay through QuantNifty's canonical execution path."""

    def __init__(self, replay_controller: ReplayController):
        self.controller = replay_controller
        self.adapter = SignalAdapter()
        self.pipeline = TradingPipeline()

    @staticmethod
    def _option_chain(ctx):
        """Read option-chain data from both RuntimeContext and mapping replays."""
        if isinstance(ctx, dict):
            return ctx.get("option_chain")
        return getattr(ctx, "option_chain", None)

    def run(self):
        print("\n========== BACKTEST START ==========\n")
        broker = self.pipeline.paper_broker
        last_option_chain = None

        while self.controller.has_next():
            ctx = self.controller.next()
            if ctx is None:
                break

            decision = self.adapter.from_context(ctx)
            if decision is not None:
                self.pipeline.process(decision=decision, snapshot=ctx)

            option_chain = self._option_chain(ctx)
            if option_chain is not None:
                last_option_chain = option_chain
            broker.update_positions(option_chain)

        finalize = getattr(broker, "close_all_positions", None)
        if callable(finalize):
            finalize(last_option_chain)

        print("\n========== BACKTEST COMPLETE ==========\n")
        return {
            "portfolio": broker.portfolio,
            "journal": broker.journal,
            "performance": broker.performance,
        }
