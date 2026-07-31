from dataclasses import dataclass


@dataclass
class DealerData:

    dealer_gamma: str

    market_mode: str

    support: float | None

    resistance: float | None

    gamma_flip: float | None

    gamma_wall: float | None

    expected_volatility: str

    mean_reversion_probability: float

    breakout_probability: float

    total_gex: float