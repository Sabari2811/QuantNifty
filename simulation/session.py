
from dataclasses import dataclass, field
from typing import Any

from simulation.state import SimulationState


@dataclass
class SimulationSession:
    """
    Represents one simulation session.

    Example
    -------
    Symbol      : NIFTY
    Date        : 2026-07-15
    Timeframe   : 5 Minute

    Contains all historical market data required
    to replay or backtest a trading session.
    """

    # ==========================================================
    # SESSION INFO
    # ==========================================================

    symbol: str = ""

    date: str = ""

    timeframe: str = ""

    expiry: str = ""

    # ==========================================================
    # MARKET DATA
    # ==========================================================

    candles: Any = None

    option_chain: Any = None

    greeks: Any = None

    # ==========================================================
    # RUNTIME
    # ==========================================================

    state: SimulationState = field(default_factory=SimulationState)