from __future__ import annotations

from core.runtime_context import RuntimeContext
from models.market_context import MarketContext

from providers.simulation_provider import SimulationProvider


class ReplayEngine:
    """
    Renders the currently selected replay snapshot
    into RuntimeContext.

    Navigation is owned by ReplaySession /
    ReplayController.
    """

    def __init__(
        self,
        provider: SimulationProvider
    ):

        self.provider = provider

        self.ctx = RuntimeContext()

    # ==========================================================
    # Render
    # ==========================================================

    def run_cycle(self):
        """
        Render current replay snapshot.

        This method NEVER changes replay position.
        """

        snapshot = self.provider.current_snapshot()

        # Preserve the authoritative replay snapshot itself.
        self.ctx.snapshot = snapshot

        self.ctx.timestamp = snapshot.timestamp
        self.ctx.cycle_no = snapshot.cycle_no
        self.ctx.symbol = snapshot.symbol

        self.ctx.spot = snapshot.spot

        self.ctx.option_chain = snapshot.option_chain.copy()

        self.ctx.greeks_df = snapshot.greeks.copy()

        # Restore the recorded analytics projection into the typed canonical
        # runtime artifact. The snapshot format remains dictionary-based for
        # backward compatibility, but replay runtime consumers must not see an
        # empty/default MarketContext when recorded analytics are available.
        self.ctx.market_context = self._restore_market_context(
            snapshot.analytics,
            spot=snapshot.spot,
            greeks=self.ctx.greeks_df,
        )
        self.ctx.analytics = snapshot.analytics

        self.ctx.decision = snapshot.decision

        self.ctx.explanation = snapshot.explanation

        self.ctx.runtime_status = "REPLAY"

        return self.ctx

    @staticmethod
    def _restore_market_context(analytics, *, spot=0.0, greeks=None):
        """Restore the typed MarketContext from a recorded analytics payload."""
        return MarketContext.from_analytics(
            analytics,
            spot=spot,
            greeks=greeks,
        )

    # ==========================================================
    # Helpers
    # ==========================================================

    def get_context(self):

        return self.ctx
