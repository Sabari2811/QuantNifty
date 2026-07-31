class TradeExecutionPipeline:
    """
    Handles the complete trade execution workflow.

    Responsibilities
    ----------------
    - Synchronize RuntimeContext
    - Risk Validation
    - Execute Paper Trades
    - Update RuntimeContext

    This class contains no market data or analytics logic.
    """

    def __init__(
        self,
        paper_broker,
        risk_manager
    ):

        self.paper_broker = paper_broker
        self.risk_manager = risk_manager

    # ==========================================================
    # Runtime Context Synchronization
    # ==========================================================

    def sync_context(self, ctx):

        broker = self.paper_broker

        ctx.portfolio = broker.portfolio_engine.portfolio

        ctx.position = getattr(broker, "position", None)

        ctx.last_trade = getattr(broker, "last_trade", None)

        ctx.journal = getattr(broker, "journal", None)

        if ctx.journal is not None:
            ctx.statistics = ctx.journal.summary()
        else:
            ctx.statistics = {}

        ctx.risk_state = self.risk_manager.state

    # ==========================================================
    # Execute Trade
    # ==========================================================

    def execute(self, ctx):

        self.sync_context(ctx)

        # Reset previous cycle status
        ctx.trade_status = ""
        ctx.trade_block_reason = ""

        if ctx.decision is None:
            return

        trade = getattr(ctx.decision, "trade", None)

        if trade is None:
            return

        # ------------------------------------------------------
        # Risk Validation
        # ------------------------------------------------------

        ok, reason = self.risk_manager.validate(
            self.paper_broker,
            ctx.decision
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