from __future__ import annotations

from analytics.intelligence.gate import IntelligenceGate


class TradeExecutionPipeline:
    """
    Handles the complete trade execution workflow.

    Responsibilities
    ----------------
    - Synchronize RuntimeContext
    - Intelligence eligibility gate
    - Risk Validation
    - Execute Paper Trades
    - Update RuntimeContext

    This class contains no market data or analytics logic.

    Execution order
    ---------------
    1. Synchronize runtime state
    2. Check for a valid decision/trade
    3. Apply Intelligence gate when Intelligence is available
    4. Apply RiskManager validation
    5. Execute through PaperBroker
    6. Synchronize runtime state again

    Intelligence does not replace RiskManager.

    Intelligence answers:
        "Is the current Intelligence state eligible to proceed?"

    RiskManager answers:
        "Is this trade allowed from a portfolio/risk perspective?"
    """

    def __init__(
        self,
        paper_broker,
        risk_manager,
        intelligence_gate=None,
    ):

        self.paper_broker = paper_broker

        self.risk_manager = risk_manager

        self.intelligence_gate = (
            intelligence_gate
            if intelligence_gate is not None
            else IntelligenceGate()
        )

    # ==========================================================
    # Runtime Context Synchronization
    # ==========================================================

    def sync_context(self, ctx):

        broker = self.paper_broker

        ctx.portfolio = (
            broker.portfolio_engine.portfolio
        )

        ctx.position = getattr(
            broker,
            "position",
            None,
        )

        ctx.last_trade = getattr(
            broker,
            "last_trade",
            None,
        )

        ctx.journal = getattr(
            broker,
            "journal",
            None,
        )

        if ctx.journal is not None:

            ctx.statistics = (
                ctx.journal.summary()
            )

        else:

            ctx.statistics = {}

        ctx.risk_state = (
            self.risk_manager.state
        )

    # ==========================================================
    # Execute Trade
    # ==========================================================

    def execute(self, ctx):

        self.sync_context(ctx)

        # ------------------------------------------------------
        # Reset previous cycle status
        # ------------------------------------------------------

        ctx.trade_status = ""

        ctx.trade_block_reason = ""

        # ------------------------------------------------------
        # Decision availability
        # ------------------------------------------------------

        if ctx.decision is None:
            return

        trade = getattr(
            ctx.decision,
            "trade",
            None,
        )

        if trade is None:
            return

        # ------------------------------------------------------
        # C8 Intelligence Gate
        # ------------------------------------------------------
        #
        # Intelligence is optional for backward compatibility.
        #
        # When Intelligence is not configured, execution follows
        # the existing RiskManager path unchanged.
        #

        if ctx.intelligence is not None:

            intelligence_result = (
                self.intelligence_gate.evaluate(
                    ctx.intelligence
                )
            )

            if not intelligence_result.allowed:

                ctx.trade_status = "BLOCKED"

                ctx.trade_block_reason = (
                    intelligence_result.reason
                )

                print()
                print("=" * 70)
                print("INTELLIGENCE GATE")
                print("=" * 70)
                print(
                    intelligence_result.reason
                )

                return

        # ------------------------------------------------------
        # Risk Validation
        # ------------------------------------------------------

        ok, reason = (
            self.risk_manager.validate(
                self.paper_broker,
                ctx.decision,
            )
        )

        if not ok:

            ctx.trade_status = "BLOCKED"

            ctx.trade_block_reason = reason

            print()
            print("=" * 70)
            print("RISK MANAGER")
            print("=" * 70)
            print(reason)

            return

        # ------------------------------------------------------
        # Execute Paper Trade
        # ------------------------------------------------------

        position = self.paper_broker.execute(
            ctx.decision
        )

        if position is not None:

            ctx.trade_status = "EXECUTED"

            ctx.position = position

        self.sync_context(ctx)