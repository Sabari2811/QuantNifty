from datetime import datetime

from models.market_context import MarketContext


class MarketSnapshot:
    """
    Central Market Snapshot.

    Every downstream module (Decision Engine, Dashboard,
    Alerts, Backtesting, Paper Trading) should consume only
    this object.

    The typed MarketContext is the canonical analytics source when supplied
    by the runtime. The analytics dictionary remains the serialized and
    backward-compatible projection for legacy callers and replay artifacts.
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

        self.market_context = None
        self.analytics = {}
        self.regime = None

    def save(
        self,
        greeks_df,
        spot,
        analytics,
        market_context=None,
    ):
        self.timestamp = datetime.now()
        self.spot = float(spot)
        self.greeks_df = (
            greeks_df.copy()
            if greeks_df is not None
            else None
        )
        self.analytics = analytics.copy()
        self.market_context = market_context
        return self

    def _canonical_or_legacy(self, field_name):
        """Read typed canonical analytics, falling back only for legacy callers."""
        if self.market_context is not None:
            return getattr(self.market_context, field_name)
        return self.analytics.get(field_name, {})

    # =====================================================
    # SHORTCUT PROPERTIES
    # =====================================================

    @property
    def dealer(self):
        return self._canonical_or_legacy("dealer")

    @property
    def probability(self):
        """Canonical probability output from the analytics pipeline."""
        return self._canonical_or_legacy("probability")

    @property
    def prediction(self):
        """Backward-compatible alias for legacy consumers."""
        return self.probability

    @property
    def signal(self):
        return self._canonical_or_legacy("signal")

    @property
    def trade_plan(self):
        return self._canonical_or_legacy("trade_plan")

    @property
    def max_pain(self):
        return self._canonical_or_legacy("max_pain")

    @property
    def market_regime(self):
        return self.regime

    @property
    def pcr(self):
        return self._canonical_or_legacy("pcr")

    @property
    def expected_move(self):
        return self._canonical_or_legacy("expected_move")

    @property
    def institutional(self):
        return self._canonical_or_legacy("institutional_score")

    @property
    def atr(self):
        return self._canonical_or_legacy("atr")

    @property
    def market_structure(self):
        return self._canonical_or_legacy("market_structure")

    @property
    def dealer_flow(self):
        return self._canonical_or_legacy("dealer_flow")

    @property
    def liquidity(self):
        return self._canonical_or_legacy("liquidity")

    @property
    def iv_skew(self):
        return self._canonical_or_legacy("iv_skew")

    @property
    def iv_smile(self):
        return self._canonical_or_legacy("iv_smile")

    @property
    def iv(self):
        """Backward-compatible legacy IV surface alias."""
        return self.analytics.get("iv", {})

    @property
    def oi_flow(self):
        """Canonical option-interest-flow output."""
        return self._canonical_or_legacy("oi_flow")

    @property
    def oi(self):
        """Backward-compatible alias for legacy consumers."""
        return self.oi_flow

    # =====================================================
    # GENERIC ACCESS
    # =====================================================

    def get(self, key, default=None):
        """Read declared canonical analytics before the legacy projection."""
        if self.market_context is not None and hasattr(self.market_context, key):
            return getattr(self.market_context, key)
        return self.analytics.get(key, default)
