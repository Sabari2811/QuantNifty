from datetime import datetime


class MarketSnapshot:
    """
    Central Market Snapshot.

    Every downstream module (Decision Engine, Dashboard,
    Alerts, Backtesting, Paper Trading) should consume only
    this object.
    """

    def __init__(self):

        self.timestamp = None

        # --------------------------------------------------
        # Live Market
        # --------------------------------------------------

        self.spot = None
        self.greeks_df = None

        # --------------------------------------------------
        # Analytics
        # --------------------------------------------------

        self.analytics = {}
        self.regime = None

    def save(
        self,
        greeks_df,
        spot,
        analytics
    ):
        self.timestamp = datetime.now()
        self.spot = float(spot)
        self.greeks_df = (
            greeks_df.copy()
            if greeks_df is not None
            else None
        )
        self.analytics = analytics.copy()
        return self

    # =====================================================
    # SHORTCUT PROPERTIES
    # =====================================================

    @property
    def dealer(self):
        return self.analytics.get("dealer", {})

    @property
    def probability(self):
        """Canonical probability output from the analytics pipeline."""
        return self.analytics.get("probability", {})

    @property
    def prediction(self):
        """Backward-compatible alias for legacy consumers."""
        return self.probability

    @property
    def trade_plan(self):
        return self.analytics.get("trade_plan", {})

    @property
    def max_pain(self):
        return self.analytics.get("max_pain", {})

    @property
    def market_regime(self):
        return self.regime

    @property
    def pcr(self):
        return self.analytics.get("pcr", {})

    @property
    def expected_move(self):
        return self.analytics.get("expected_move", {})

    @property
    def institutional(self):
        return self.analytics.get("institutional_score", {})

    @property
    def atr(self):
        return self.analytics.get("atr", {})

    @property
    def market_structure(self):
        return self.analytics.get("market_structure", {})

    @property
    def dealer_flow(self):
        return self.analytics.get("dealer_flow", {})

    @property
    def liquidity(self):
        return self.analytics.get("liquidity", {})

    @property
    def iv(self):
        return self.analytics.get("iv", {})

    @property
    def oi_flow(self):
        """Canonical option-interest-flow output."""
        return self.analytics.get("oi_flow", {})

    @property
    def oi(self):
        """Backward-compatible alias for legacy consumers."""
        return self.oi_flow

    # =====================================================
    # GENERIC ACCESS
    # =====================================================

    def get(self, key, default=None):
        return self.analytics.get(key, default)
