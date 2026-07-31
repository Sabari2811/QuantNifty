from __future__ import annotations

from providers.base_provider import BaseProvider
from runtime.runtime_mode import RuntimeMode
from simulation.replay_source import ReplaySource


class SimulationProvider(BaseProvider):
    """
    Market data provider backed by recorded snapshots.

    Implements the same BaseProvider interface as the live
    provider, allowing LiveEngine to run without knowing
    whether market data is coming from a live broker or
    replayed snapshots.
    """

    def __init__(
        self,
        replay_source: ReplaySource,
        runtime_mode: RuntimeMode = RuntimeMode.REPLAY_FAST
    ):

        self.source = replay_source

        self.snapshot = None

        self._runtime_mode = runtime_mode

    # ==========================================================
    # Runtime Mode
    # ==========================================================

    @property
    def runtime_mode(self):

        return self._runtime_mode

    # ==========================================================
    # BaseProvider Interface
    # ==========================================================

    def connect(self):
        """
        Replay mode requires no external connection.
        """
        return True

    def get_spot_price(self, symbol=None):
        """
        Return spot price from current replay snapshot.
        """
        self._ensure_snapshot()

        return self.snapshot.spot

    def get_historical_data(self, *args, **kwargs):
        """
        Historical data is unavailable during replay.

        In REPLAY_FAST mode, analytics are already recorded.

        In REPLAY_RECOMPUTE mode this method can later be
        extended to load historical candles from disk.
        """
        raise NotImplementedError(
            "Historical data is not supported by SimulationProvider."
        )

    def get_option_chain(self, *args, **kwargs):
        """
        Return recorded option chain.
        """
        self._ensure_snapshot()

        return self.snapshot.option_chain.copy()

    # ==========================================================
    # Replay Controls
    # ==========================================================

    def next_cycle(self):
        """
        Advance to the next recorded snapshot.
        """

        if not self.source.has_next():

            raise StopIteration(
                "Replay completed."
            )

        self.snapshot = self.source.next()

        return self.snapshot

    def reset(self):
        """
        Restart replay from the beginning.
        """

        self.source.reset()

        self.snapshot = None

    # ==========================================================
    # Snapshot Accessors
    # ==========================================================

    def get_runtime(self):

        self._ensure_snapshot()

        return self.snapshot.runtime

    def get_greeks(self):

        self._ensure_snapshot()

        return self.snapshot.greeks.copy()

    def get_analytics(self):

        self._ensure_snapshot()

        return self.snapshot.analytics

    def get_decision(self):

        self._ensure_snapshot()

        return self.snapshot.decision

    def get_explanation(self):

        self._ensure_snapshot()

        return self.snapshot.explanation

    # ==========================================================
    # Convenience Properties
    # ==========================================================

    @property
    def timestamp(self):

        self._ensure_snapshot()

        return self.snapshot.timestamp

    @property
    def cycle_no(self):

        self._ensure_snapshot()

        return self.snapshot.cycle_no

    @property
    def symbol(self):

        self._ensure_snapshot()

        return self.snapshot.symbol

    # ==========================================================
    # Internal
    # ==========================================================

    def _ensure_snapshot(self):
        """
        Lazily load the first snapshot.
        """

        if self.snapshot is None:

            if not self.source.has_next():

                raise StopIteration(
                    "Replay completed."
                )

            self.snapshot = self.source.next()