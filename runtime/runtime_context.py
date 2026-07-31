from __future__ import annotations

"""
==========================================================

Runtime Context

Holds the application's runtime state.

Does NOT create dependencies.

Dependencies are injected from CompositionRoot.

==========================================================
"""


class RuntimeContext:

    def __init__(
        self,
        composition,
    ):

        #
        # Composition Root
        #

        self.composition = composition

        #
        # Infrastructure
        #

        self.paper_broker = composition.paper_broker

        #
        # Application Services
        #

        self.intelligence_service = (
            composition.intelligence_service
        )

    # ===================================================
    # Broker
    # ===================================================

    @property
    def portfolio(self):

        return self.paper_broker.portfolio

    @property
    def journal(self):

        return self.paper_broker.journal

    @property
    def position(self):

        return self.paper_broker.position

    @property
    def last_trade(self):

        return self.paper_broker.last_trade

    @property
    def performance(self):

        return self.paper_broker.performance