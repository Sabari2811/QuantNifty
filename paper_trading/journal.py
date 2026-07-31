from paper_trading.models import (
    PaperPosition,
    TradeRecord,
)


class TradeJournal:
    """
    Maintains the completed paper-trade history.

    Responsibilities
    ----------------
    - Store completed trades
    - Provide journal access
    - Provide portfolio statistics

    Does NOT
    ----------
    - Execute trades
    - Calculate MTM
    - Manage positions
    """

    def __init__(self):

        self.records = []

    # ==================================================
    # RECORD TRADE
    # ==================================================

    def record(
        self,
        position: PaperPosition,
        exit_reason: str,
    ) -> TradeRecord:

        holding = (
            position.exit_time
            - position.order.order_time
        ).total_seconds()

        record = TradeRecord(

            order_id=position.order.order_id,

            strategy_name=position.strategy_name,

            signal=position.order.signal,

            option_type=position.order.option_type,

            strike=position.order.strike,

            quantity=position.order.quantity,

            entry_price=position.order.entry_price,

            exit_price=position.exit_price,

            pnl=position.pnl,

            entry_time=position.order.order_time,

            exit_time=position.exit_time,

            confidence=position.confidence,

            risk_reward=position.risk_reward,

            probability=0.0,

            regime="",

            dealer_position="",

            entry_candle=position.entry_candle,

            exit_candle=position.exit_candle,

            exit_reason=exit_reason,

            holding_seconds=holding,

        )

        self.records.append(record)

        return record

    # ==================================================
    # JOURNAL
    # ==================================================

    def all_trades(self):

        return sorted(

            self.records,

            key=lambda t: t.exit_time,

            reverse=True,

        )

    def last_trade(self):

        if not self.records:
            return None

        return self.all_trades()[0]

    def recent_trades(self, limit=10):

        return self.all_trades()[:limit]

    # ==================================================
    # STATISTICS
    # ==================================================

    def summary(self):

        trades = self.records

        total = len(trades)

        winners = [
            t for t in trades
            if t.pnl > 0
        ]

        losers = [
            t for t in trades
            if t.pnl < 0
        ]

        gross_profit = sum(
            t.pnl for t in winners
        )

        gross_loss = abs(sum(
            t.pnl for t in losers
        ))

        avg_winner = (
            gross_profit / len(winners)
            if winners else 0
        )

        avg_loser = (
            gross_loss / len(losers)
            if losers else 0
        )

        profit_factor = (
            gross_profit / gross_loss
            if gross_loss > 0
            else 0
        )

        win_rate = (
            len(winners) * 100 / total
            if total
            else 0
        )

        return {

            "total_trades": total,

            "winning_trades": len(winners),

            "losing_trades": len(losers),

            "win_rate": round(win_rate, 2),

            "gross_profit": gross_profit,

            "gross_loss": gross_loss,

            "profit_factor": round(profit_factor, 2),

            "average_winner": round(avg_winner, 2),

            "average_loser": round(avg_loser, 2),

            "total_pnl": sum(
                t.pnl
                for t in trades
            ),

        }