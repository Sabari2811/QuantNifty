from __future__ import annotations

from dataclasses import dataclass

from config.trading_config import TradingConfig


@dataclass(frozen=True)
class DeltaRiskModel:
    """Translate bounded NIFTY movement into option-premium levels via delta."""

    max_daily_underlying_points: float = TradingConfig.MAX_DAILY_UNDERLYING_MOVE
    max_trade_underlying_points: float = TradingConfig.MAX_TRADE_UNDERLYING_MOVE
    stop_underlying_points: float = TradingConfig.STOP_UNDERLYING_POINTS
    target1_underlying_points: float = TradingConfig.TARGET1_UNDERLYING_POINTS
    target2_underlying_points: float = TradingConfig.TARGET2_UNDERLYING_POINTS

    def __post_init__(self):
        if self.max_trade_underlying_points > self.max_daily_underlying_points:
            raise ValueError("Trade movement cap cannot exceed daily movement cap")
        if self.stop_underlying_points <= 0:
            raise ValueError("Stop movement must be positive")
        if self.target1_underlying_points <= 0 or self.target2_underlying_points <= 0:
            raise ValueError("Target movement must be positive")
        if self.stop_underlying_points > self.max_trade_underlying_points:
            raise ValueError("Stop movement exceeds trade movement cap")
        if self.target1_underlying_points > self.max_trade_underlying_points:
            raise ValueError("Target1 movement exceeds trade movement cap")
        if self.target2_underlying_points > self.max_trade_underlying_points:
            raise ValueError("Target2 movement exceeds trade movement cap")

    @staticmethod
    def _delta(delta: float) -> float:
        try:
            value = abs(float(delta))
        except (TypeError, ValueError):
            return 0.0
        return min(value, 1.0)

    def premium_move(self, delta: float, underlying_points: float) -> float:
        """First-order option-premium movement approximation: |delta| * dS."""
        return self._delta(delta) * float(underlying_points)

    def levels(self, entry: float, delta: float) -> tuple[float, float, float]:
        """Return (stop, target1, target2) for a long option premium."""
        premium = float(entry)
        d = self._delta(delta)
        if premium <= 0 or d <= 0:
            return 0.0, 0.0, 0.0

        stop_move = self.premium_move(d, self.stop_underlying_points)
        target1_move = self.premium_move(d, self.target1_underlying_points)
        target2_move = self.premium_move(d, self.target2_underlying_points)

        stop = max(0.05, premium - stop_move)
        target1 = premium + target1_move
        target2 = premium + target2_move
        return round(stop, 2), round(target1, 2), round(target2, 2)
