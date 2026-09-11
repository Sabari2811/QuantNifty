from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from zoneinfo import ZoneInfo

from config.trading_config import TradingConfig


IST = ZoneInfo("Asia/Kolkata")


@dataclass(frozen=True)
class NiftyPolicy:
    """Single source of truth for the NIFTY-only intraday trading contract."""

    symbol: str = "NIFTY"
    max_daily_move: float = TradingConfig.MAX_DAILY_UNDERLYING_MOVE
    max_trade_move: float = TradingConfig.MAX_TRADE_UNDERLYING_MOVE
    max_trades_per_day: int = TradingConfig.MAX_TRADES_PER_DAY
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
        """Enforce the strategy's absolute intraday NIFTY movement ceiling."""
        if session_open is None or spot is None:
            return True, ""
        try:
            opening = float(session_open)
            current = float(spot)
        except (TypeError, ValueError):
            return False, "NIFTY_SESSION_MOVE_UNAVAILABLE"
        if opening <= 0 or current <= 0:
            return False, "NIFTY_SESSION_MOVE_UNAVAILABLE"
        move = abs(current - opening)
        if move > self.max_daily_move:
            return False, f"NIFTY_DAILY_MOVE_BOUND_EXCEEDED:{move:.2f}"
        return True, ""

    def session_open_from_snapshot(self, snapshot) -> float | None:
        """Extract a real session-open observation without fabricating one."""
        context = getattr(snapshot, "market_context", None)
        candidates = []
        if context is not None:
            technical = getattr(context, "technical", {}) or {}
            candidates.extend([
                technical.get("session_open"),
                technical.get("day_open"),
                technical.get("open"),
            ])
        analytics = getattr(snapshot, "analytics", {}) or {}
        technical = analytics.get("technical", {}) or {}
        candidates.extend([
            analytics.get("session_open"),
            analytics.get("day_open"),
            technical.get("session_open"),
            technical.get("day_open"),
            technical.get("open"),
        ])
        for value in candidates:
            try:
                parsed = float(value)
                if parsed > 0:
                    return parsed
            except (TypeError, ValueError):
                continue
        return None

    def validate_snapshot_move(self, snapshot) -> tuple[bool, str]:
        """Validate current NIFTY movement when a real session-open is present."""
        return self.validate_daily_move(
            self.session_open_from_snapshot(snapshot),
            getattr(snapshot, "spot", None),
        )

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
            "max_daily_underlying_move_points": self.max_daily_move,
            "max_trade_underlying_move_points": self.max_trade_move,
            "max_trades_per_day": self.max_trades_per_day,
            "entry_cutoff_ist": self.entry_cutoff.strftime("%H:%M"),
            "execution": "BUY_NIFTY_CE_OR_PE",
            "overnight_position": False,
        }
