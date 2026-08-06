from __future__ import annotations

from providers.base_provider import BaseProvider
from runtime.runtime_mode import RuntimeMode
from simulation.replay_source import ReplaySource


class SimulationProvider(BaseProvider):
    """
    Market data provider backed by recorded snapshots.

    Unlike the live provider, this provider NEVER changes
    replay position.

    Navigation belongs exclusively to ReplaySession /
    ReplayController.
    """

    def __init__(
        self,
        replay_source: ReplaySource,
        runtime_mode: RuntimeMode = RuntimeMode.REPLAY_FAST
    ):

        self.source = replay_source

        self._runtime_mode = runtime_mode

    # ==========================================================
    # Runtime
    # ==========================================================

    @property
    def runtime_mode(self):

        return self._runtime_mode

    # ==========================================================
    # Provider
    # ==========================================================

    def connect(self):

        return True

    # ==========================================================
    # Snapshot
    # ==========================================================

    def current_snapshot(self):

        return self.source.current()

    # ==========================================================
    # Live Provider Interface
    # ==========================================================

    def get_spot_price(self, symbol=None):

        return self.current_snapshot().spot

    def get_option_chain(self, *args, **kwargs):

        return self.current_snapshot().option_chain.copy()

    def get_historical_data(self, *args, **kwargs):

        raise NotImplementedError(
            "Historical data unavailable in replay."
        )

    # ==========================================================
    # Snapshot Accessors
    # ==========================================================

    def get_runtime(self):

        return self.current_snapshot().runtime

    def get_greeks(self):

        return self.current_snapshot().greeks.copy()

    def get_analytics(self):

        return self.current_snapshot().analytics

    def get_decision(self):

        return self.current_snapshot().decision

    def get_explanation(self):

        return self.current_snapshot().explanation

    # ==========================================================
    # Convenience
    # ==========================================================

    @property
    def timestamp(self):

        return self.current_snapshot().timestamp

    @property
    def cycle_no(self):

        return self.current_snapshot().cycle_no

    @property
    def symbol(self):

        return self.current_snapshot().symbol