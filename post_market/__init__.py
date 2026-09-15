"""Post-market NIFTY strategy replay lab.

This package is deliberately isolated from the live decision/execution path.
It consumes normalized intraday spot + option snapshots and produces deterministic
trade-by-trade results for research. No broker orders are placed.
"""

from .strategy_lab import run_post_market_replay

__all__ = ["run_post_market_replay"]
