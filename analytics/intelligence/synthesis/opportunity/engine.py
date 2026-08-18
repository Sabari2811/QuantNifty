from __future__ import annotations

from dataclasses import dataclass

from decision.models import Decision


@dataclass(frozen=True, slots=True)
class OpportunityQuality:
    """Compatibility-first opportunity quality assessment."""

    score: float = 0.0

    risk_reward_score: float = 0.0
    volatility_score: float = 0.0
    open_interest_score: float = 0.0
    volume_score: float = 0.0
    delta_score: float = 0.0

    contract_available: bool = False

    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in (
            "score",
            "risk_reward_score",
            "volatility_score",
            "open_interest_score",
            "volume_score",
            "delta_score",
        ):
            value = getattr(self, name)

            if not 0.0 <= value <= 100.0:
                raise ValueError(
                    f"{name} must be between 0 and 100"
                )


class OpportunityQualityEngine:
    """
    Scores the quality of an available option opportunity.

    This preserves the validated legacy TradeQualityEngine
    scoring contract while exposing a structured Intelligence-layer
    result.

    Legacy scoring:

        Risk/Reward -> 30
        IV          -> 20
        OI          -> 20
        Volume      -> 20
        Delta       -> 10
        ----------------
        Maximum     -> 100

    This engine does not make the final trade decision.
    """

    def evaluate(
        self,
        decision: Decision,
    ) -> OpportunityQuality:
        trade = decision.trade
        contract = trade.contract

        if contract is None:
            return OpportunityQuality(
                score=0.0,
                contract_available=False,
                reasons=(
                    "No option contract is available",
                ),
            )

        risk_reward_score = self._risk_reward_score(
            trade.risk_reward
        )

        volatility_score = self._volatility_score(
            contract.iv
        )

        open_interest_score = self._open_interest_score(
            contract.oi
        )

        volume_score = self._volume_score(
            contract.volume
        )

        delta_score = self._delta_score(
            contract.delta
        )

        score = (
            risk_reward_score
            + volatility_score
            + open_interest_score
            + volume_score
            + delta_score
        )

        reasons = self._build_reasons(
            trade.risk_reward,
            contract.iv,
            contract.oi,
            contract.volume,
            contract.delta,
            risk_reward_score,
            volatility_score,
            open_interest_score,
            volume_score,
            delta_score,
        )

        return OpportunityQuality(
            score=min(100.0, score),
            risk_reward_score=risk_reward_score,
            volatility_score=volatility_score,
            open_interest_score=open_interest_score,
            volume_score=volume_score,
            delta_score=delta_score,
            contract_available=True,
            reasons=reasons,
        )

    def score(
        self,
        decision: Decision,
    ) -> float:
        """
        Compatibility helper returning only the 0-100 score.
        """

        return self.evaluate(decision).score

    @staticmethod
    def _risk_reward_score(
        risk_reward: float,
    ) -> float:
        if risk_reward >= 2.0:
            return 30.0

        if risk_reward >= 1.5:
            return 20.0

        if risk_reward >= 1.0:
            return 10.0

        return 0.0

    @staticmethod
    def _volatility_score(
        iv: float,
    ) -> float:
        if 10.0 <= iv <= 25.0:
            return 20.0

        if 5.0 <= iv < 10.0:
            return 10.0

        return 0.0

    @staticmethod
    def _open_interest_score(
        oi: int,
    ) -> float:
        if oi >= 100_000:
            return 20.0

        if oi >= 50_000:
            return 10.0

        return 0.0

    @staticmethod
    def _volume_score(
        volume: int,
    ) -> float:
        if volume >= 50_000:
            return 20.0

        if volume >= 20_000:
            return 10.0

        return 0.0

    @staticmethod
    def _delta_score(
        delta: float,
    ) -> float:
        if 0.30 <= abs(delta) <= 0.70:
            return 10.0

        return 0.0

    @staticmethod
    def _build_reasons(
        risk_reward: float,
        iv: float,
        oi: int,
        volume: int,
        delta: float,
        risk_reward_score: float,
        volatility_score: float,
        open_interest_score: float,
        volume_score: float,
        delta_score: float,
    ) -> tuple[str, ...]:
        reasons: list[str] = []

        if risk_reward_score:
            reasons.append(
                f"Risk/reward {risk_reward:.2f} "
                f"contributes {risk_reward_score:.0f}"
            )
        else:
            reasons.append(
                f"Risk/reward {risk_reward:.2f} "
                "contributes 0"
            )

        if volatility_score:
            reasons.append(
                f"IV {iv:.2f} contributes "
                f"{volatility_score:.0f}"
            )
        else:
            reasons.append(
                f"IV {iv:.2f} contributes 0"
            )

        if open_interest_score:
            reasons.append(
                f"OI {oi} contributes "
                f"{open_interest_score:.0f}"
            )
        else:
            reasons.append(
                f"OI {oi} contributes 0"
            )

        if volume_score:
            reasons.append(
                f"Volume {volume} contributes "
                f"{volume_score:.0f}"
            )
        else:
            reasons.append(
                f"Volume {volume} contributes 0"
            )

        if delta_score:
            reasons.append(
                f"Delta {delta:.2f} contributes "
                f"{delta_score:.0f}"
            )
        else:
            reasons.append(
                f"Delta {delta:.2f} contributes 0"
            )

        return tuple(reasons)