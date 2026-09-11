from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from zoneinfo import ZoneInfo

from config.trading_config import TradingConfig


IST = ZoneInfo("Asia/Kolkata")


@dataclass(frozen=True)
class NiftyPolicy:
    """Single source of truth for the NIFTY-only trading contract.

    QuantNifty is deliberately not a multi-asset strategy. Direction is always
    expressed as a NIFTY underlying view and execution is limited to buying the
    corresponding NIFTY CE/PE option.
    """

    symbol: str = "NIFTY"
    max_daily_move: float = TradingConfig.MAX_DAILY_UNDERLYING_MOVE
    max_trade_move: float = TradingConfig.MAX_TRADE_UNDERLYING_MOVE
    entry_cutoff: time = time(
        TradingConfig.INTRADAY_FORCE_EXIT_HOUR,
        TradingConfig.INTRADAY_FORCE_EXIT_MINUTE,
    )

    def validate_symbol(self, symbol: str | None) -> tuple[bool, str]:
        value = str(symbol or self.symbol).strip().upper()
        if value != self.symbol:
            return False, f"NIFTY_ONLY_SYMBOL_REQUIRED:{value}"
        return True, ""

    def validate_option(self, option_type: str | None) -> tuple[bool, str]:
        value = str(option_type or "").strip().upper()
        if value not in {"CE", "PE"}:
            return False, "NIFTY_OPTION_MUST_BE_CE_OR_PE"
        return True, ""

    def validate_delta(self, delta: float | None) -> tuple[bool, str]:
        try:
            value = abs(float(delta))
        except (TypeError, ValueError):
            return False, "NIFTY_OPTION_DELTA_UNAVAILABLE"
        if not 0.05 <= value <= 1.0:
            return False, "NIFTY_OPTION_DELTA_OUTSIDE_EXECUTION_RANGE"
        return True, ""

    def validate_daily_move(self, session_open: float | None, spot: float | None) -> tuple[bool, str]:
        """Guard the NIFTY risk model against an already-exhausted daily move."""
        if session_open is None or spot is None:
            return True, ""
        try:
            move = abs(float(spot) - float(session_open))
        except (TypeError, ValueError):
            return False, "NIFTY_SESSION_MOVE_UNAVAILABLE"
        if move > self.max_daily_move:
            return False, f"NIFTY_DAILY_MOVE_BOUND_EXCEEDED:{move:.2f}"
        return True, ""

    def entry_allowed(self, now: datetime | None = None) -> tuple[bool, str]:
        current = (now or datetime.now(IST)).astimezone(IST)
        if current.weekday() >= 5:
            return False, "NIFTY_MARKET_CLOSED"
        if current.time() >= self.entry_cutoff:
            return False, "NIFTY_INTRADAY_ENTRY_CUTOFF"
        return True, ""

    def metadata(self) -> dict:
        return {
            "underlying": self.symbol,
            "max_daily_move_points": self.max_daily_move,
            "max_trade_move_points": self.max_trade_move,
            "entry_cutoff_ist": self.entry_cutoff.strftime("%H:%M"),
            "execution": "BUY_NIFTY_CE_OR_PE",
            "overnight_position": False,
        }
