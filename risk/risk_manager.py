from datetime import datetime, timedelta

from risk.risk_state import RiskState


class RiskManager:

    MAX_DAILY_LOSS = -5000
    MAX_TRADES_PER_DAY = 10
    MAX_OPEN_POSITIONS = 1
    MAX_CAPITAL_PER_TRADE = 100000
    MAX_CAPITAL_USAGE = 0.40
    MAX_CONSECUTIVE_LOSSES = 3
    COOLDOWN_MINUTES = 30

    def __init__(self):
        self.state = RiskState()

    def validate(self, broker, decision, context=None):
        self._reset_if_new_day()

        if decision is None:
            return False, "Decision Unavailable"

        ok, msg = self._market_data_readiness(context)
        if not ok:
            return False, msg

        ok, msg = self._market_hours()
        if not ok:
            return False, msg

        ok, msg = self._daily_loss()
        if not ok:
            return False, msg

        ok, msg = self._cooldown()
        if not ok:
            return False, msg

        ok, msg = self._trade_limit()
        if not ok:
            return False, msg

        ok, msg = self._open_position_limit(broker)
        if not ok:
            return False, msg

        ok, msg = self._capital_per_trade(broker, decision)
        if not ok:
            return False, msg

        ok, msg = self._capital_utilization(broker)
        if not ok:
            return False, msg

        ok, msg = self._loss_limit()
        if not ok:
            return False, msg

        return True, ""

    def _market_data_readiness(self, context):
        if context is None:
            return True, ""

        provenance = getattr(context, "data_provenance", None)
        if provenance is None:
            return False, "Market Data Provenance Unavailable"

        readiness = (
            ("spot", getattr(provenance.spot, "freshness_verified", False), getattr(provenance.spot, "integrity_status", "VALID")),
            ("option_chain", getattr(provenance.option_chain, "freshness_verified", False), getattr(provenance.option_chain, "integrity_status", "VALID")),
        )
        for name, fresh, integrity in readiness:
            if not fresh:
                return False, f"{name} Market Data Not Fresh"
            if integrity == "INVALID":
                return False, f"{name} Market Data Invalid"

        return True, ""

    def on_trade_closed(self, position):
        self.state.trades_today += 1
        self.state.todays_pnl += position.pnl

        if position.pnl < 0:
            self.state.consecutive_losses += 1
            if self.state.consecutive_losses >= self.MAX_CONSECUTIVE_LOSSES:
                self.state.cooldown_until = (
                    datetime.now() + timedelta(minutes=self.COOLDOWN_MINUTES)
                )
        else:
            self.state.consecutive_losses = 0

    def _market_hours(self):
        now = datetime.now()
        start = now.replace(hour=9, minute=15, second=0)
        end = now.replace(hour=15, minute=15, second=0)
        if now < start or now > end:
            return False, "Outside Market Hours"
        return True, ""

    def _daily_loss(self):
        if self.state.todays_pnl <= self.MAX_DAILY_LOSS:
            return False, "Daily Loss Limit Hit"
        return True, ""

    def _trade_limit(self):
        if self.state.trades_today >= self.MAX_TRADES_PER_DAY:
            return False, "Trade Limit Reached"
        return True, ""

    def _open_position_limit(self, broker):
        if len(broker.portfolio.open_positions) >= self.MAX_OPEN_POSITIONS:
            return False, "Maximum Open Positions"
        return True, ""

    def _capital_per_trade(self, broker, decision):
        trade = decision.trade
        execution = trade.execution
        investment = trade.entry * execution.lot_size * execution.lots
        if investment > self.MAX_CAPITAL_PER_TRADE:
            return False, "Capital Per Trade Limit"
        return True, ""

    def _capital_utilization(self, broker):
        capital = broker.portfolio.capital
        if capital <= 0:
            return False, "Invalid Capital"
        if broker.portfolio.invested_amount / capital > self.MAX_CAPITAL_USAGE:
            return False, "Capital Usage Limit"
        return True, ""

    def _loss_limit(self):
        if self.state.todays_pnl <= self.MAX_DAILY_LOSS:
            return False, "Daily Loss Limit Hit"
        return True, ""

    def _cooldown(self):
        if self.state.cooldown_until is not None and datetime.now() < self.state.cooldown_until:
            return False, "Risk Cooldown Active"
        return True, ""

    def _reset_if_new_day(self):
        # Preserve existing state-reset behavior when present.
        reset = getattr(self.state, "reset_if_new_day", None)
        if callable(reset):
            reset()
