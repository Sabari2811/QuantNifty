from __future__ import annotations

from analytics.intelligence.gate import IntelligenceGate


class TradeExecutionPipeline:
    """
    Handles the complete trade execution workflow.

    Responsibilities
    ----------------
    - Synchronize RuntimeContext
    - Intelligence eligibility gate
    - Decision/Intelligence consistency and actionability gate
    - Risk Validation
    - Execute Paper Trades
    - Update RuntimeContext

    A broker returning ``None`` after all pre-trade gates pass is an execution
    rejection, not a successful execution and not an implicit no-op. The
    runtime context records that outcome explicitly so downstream UI,
    recording, and operational reconciliation cannot mistake it for an
    executed trade.
    """

    def __init__(self, paper_broker, risk_manager, intelligence_gate=None):
        self.paper_broker = paper_broker
        self.risk_manager = risk_manager
        self.intelligence_gate = intelligence_gate if intelligence_gate is not None else IntelligenceGate()

    def sync_context(self, ctx):
        broker = self.paper_broker
        ctx.portfolio = broker.portfolio_engine.portfolio
        ctx.position = getattr(broker, "position", None)
        ctx.last_trade = getattr(broker, "last_trade", None)
        ctx.journal = getattr(broker, "journal", None)
        ctx.statistics = ctx.journal.summary() if ctx.journal is not None else {}
        ctx.risk_state = self.risk_manager.state

    def execute(self, ctx):
        self.sync_context(ctx)
        ctx.trade_status = ""
        ctx.trade_block_reason = ""

        if ctx.decision is None:
            return
        trade = getattr(ctx.decision, "trade", None)
        if trade is None:
            return

        if ctx.intelligence is not None:
            intelligence_result = self.intelligence_gate.evaluate(ctx.intelligence)
            if not intelligence_result.allowed:
                ctx.trade_status = "BLOCKED"
                ctx.trade_block_reason = intelligence_result.reason
                print("\n" + "=" * 70)
                print("INTELLIGENCE GATE")
                print("=" * 70)
                print(intelligence_result.reason)
                return

            consistency = getattr(ctx, "decision_intelligence_consistency", None)
            if consistency is not None and not consistency.actionable:
                ctx.trade_status = "BLOCKED"
                ctx.trade_block_reason = consistency.reason
                semantic_status = getattr(consistency, "semantic_status", "CONFLICT")
                title = (
                    "DECISION / INTELLIGENCE DEFERRAL GATE"
                    if semantic_status == "DEFERRED"
                    else "DECISION / INTELLIGENCE CONSISTENCY GATE"
                )
                print("\n" + "=" * 70)
                print(title)
                print("=" * 70)
                print(consistency.reason)
                return

        ok, reason = self.risk_manager.validate(self.paper_broker, ctx.decision)
        if not ok:
            ctx.trade_status = "BLOCKED"
            ctx.trade_block_reason = reason
            print("\n" + "=" * 70)
            print("RISK MANAGER")
            print("=" * 70)
            print(reason)
            return

        position = self.paper_broker.execute(ctx.decision)
        if position is not None:
            ctx.trade_status = "EXECUTED"
            ctx.position = position
        else:
            ctx.trade_status = "REJECTED"
            ctx.trade_block_reason = "Broker rejected trade execution."
            print("\n" + "=" * 70)
            print("BROKER EXECUTION")
            print("=" * 70)
            print(ctx.trade_block_reason)

        self.sync_context(ctx)
