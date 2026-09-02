from types import SimpleNamespace

from dashboard.components.market_regime import render


def test_market_regime_renders_missing_probability_and_dealer_values(monkeypatch):
    class Column:
        def __init__(self):
            self.metrics = []

        def metric(self, label, value):
            self.metrics.append((label, value))

    groups = iter(
        [
            [Column() for _ in range(4)],
            [Column() for _ in range(4)],
            [Column() for _ in range(3)],
        ]
    )
    rendered = []

    def columns(count):
        group = next(groups)
        assert len(group) == count
        rendered.append(group)
        return group

    monkeypatch.setattr("dashboard.components.market_regime.st.columns", columns)
    monkeypatch.setattr("dashboard.components.market_regime.st.subheader", lambda *args, **kwargs: None)
    monkeypatch.setattr("dashboard.components.market_regime.st.divider", lambda: None)

    dashboard = SimpleNamespace(
        dealer=SimpleNamespace(
            dealer_gamma=None,
            market_mode=None,
            expected_volatility=None,
            gamma_flip=None,
            gamma_wall=None,
            mean_reversion_probability=None,
            breakout_probability=None,
            total_gex=None,
        ),
        probability={},
    )

    render(dashboard)

    first, second, third = rendered
    assert ("Dealer Gamma", "UNAVAILABLE") in first[0].metrics
    assert ("Market Mode", "UNAVAILABLE") in first[1].metrics
    assert ("Expected Volatility", "UNAVAILABLE") in first[2].metrics
    assert ("Confidence", "UNAVAILABLE") in first[3].metrics
    assert ("Bullish", "UNAVAILABLE%") in second[0].metrics
    assert ("Bearish", "UNAVAILABLE%") in second[1].metrics
    assert ("Mean Reversion", "UNAVAILABLE%") in second[2].metrics
    assert ("Breakout", "UNAVAILABLE%") in second[3].metrics
    assert ("Total GEX", "UNAVAILABLE") in third[2].metrics
