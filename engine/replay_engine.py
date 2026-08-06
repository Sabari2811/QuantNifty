from __future__ import annotations

from core.runtime_context import RuntimeContext

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

        self.ctx.timestamp = snapshot.timestamp
        self.ctx.cycle_no = snapshot.cycle_no
        self.ctx.symbol = snapshot.symbol

        self.ctx.spot = snapshot.spot

        self.ctx.option_chain = snapshot.option_chain.copy()

        self.ctx.greeks_df = snapshot.greeks.copy()

        self.ctx.analytics = snapshot.analytics

        self.ctx.decision = snapshot.decision

        self.ctx.explanation = snapshot.explanation

        self.ctx.runtime_status = "REPLAY"

        return self.ctx

    # ==========================================================
    # Helpers
    # ==========================================================

    def get_context(self):

        return self.ctx