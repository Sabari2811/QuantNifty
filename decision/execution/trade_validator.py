from config.trading_config import TradingConfig
from decision.validation_result import ValidationResult


class TradeValidator:
    """Final validation before execution using centralized NIFTY thresholds."""

    def validate(self, decision):
        trade = decision.trade
        contract = trade.contract
        warnings = []
        valid = True

        if trade.risk_reward <= TradingConfig.MIN_RISK_REWARD:
            valid = False
            warnings.append(
                f"Risk/Reward must be greater than {TradingConfig.MIN_RISK_REWARD}"
            )

        if trade.entry < TradingConfig.MIN_OPTION_PREMIUM:
            valid = False
            warnings.append("Premium too low")

        if contract.oi < TradingConfig.MIN_OPTION_OI:
            valid = False
            warnings.append("Low Open Interest")

        if contract.volume < TradingConfig.MIN_OPTION_VOLUME:
            valid = False
            warnings.append("Low Volume")

        # Premium stop risk is expressed as a percentage of entry premium.
        if trade.entry and trade.stop_loss is not None:
            option_risk_pct = (
                abs(trade.entry - trade.stop_loss) / trade.entry
            ) * 100.0
            if option_risk_pct > TradingConfig.MAX_OPTION_RISK_PERCENT:
                valid = False
                warnings.append("Option risk exceeds configured maximum")

        quality_score = decision.score.get("quality_score")
        if quality_score is None:
            quality_score = decision.score.get("final", 0)
        quality_score = abs(float(quality_score))

        if quality_score >= 120:
            grade, confidence, risk_multiplier = "A+", 100, 1.00
        elif quality_score >= 100:
            grade, confidence, risk_multiplier = "A", 90, 0.75
        elif quality_score >= 80:
            grade, confidence, risk_multiplier = "B", 80, 0.50
        elif quality_score >= 60:
            grade, confidence, risk_multiplier = "C", 70, 0.25
        elif quality_score >= 40:
            grade, confidence, risk_multiplier = "D", 50, 0.00
            valid = False
        else:
            grade, confidence, risk_multiplier = "F", 25, 0.00
            valid = False

        return ValidationResult(
            valid=valid,
            grade=grade,
            confidence=confidence,
            risk_multiplier=risk_multiplier,
            warnings=warnings,
        )
