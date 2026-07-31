from enum import Enum


class RuntimeMode(str, Enum):
    """
    Runtime execution modes.

    LIVE
        Uses live market data from broker.

    REPLAY_FAST
        Loads recorded analytics without recomputing.

    REPLAY_RECOMPUTE
        Loads recorded market data and recomputes
        analytics, decisions and trades.
    """

    LIVE = "LIVE"

    REPLAY_FAST = "REPLAY_FAST"

    REPLAY_RECOMPUTE = "REPLAY_RECOMPUTE"