from types import SimpleNamespace

from dashboard.components.market_banner import render


def test_market_banner_renders_degraded_dashboard_without_canonical_signal(monkeypatch):
    class Column:
        def __init__(self):
            self.warning_values = []
            self.metric_values = []
            self.success_values = []
            self.error_values = []

        def warning(self, value):
            self.warning_values.append(value)

        def success(self, value):
            self.success_values.append(value)

        def error(self, value):
            self.error_values.append(value)

        def metric(self, label, value):
            self.metric_values.append((label, value))

    columns = [Column() for _ in range(9)]

    iterator = iter(columns)
    monkeypatch.setattr("dashboard.components.market_banner.st.columns", lambda count: [next(iterator) for _ in range(count)])
    monkeypatch.setattr("dashboard.components.market_banner.st.markdown", lambda *args, **kwargs: None)
    monkeypatch.setattr("dashboard.components.market_banner.st.divider", lambda: None)

    dashboard = SimpleNamespace(
        dealer=SimpleNamespace(
            dealer_gamma="POSITIVE",
            market_mode="RANGE",
            gamma_flip=None,
            gamma_wall=None,
        ),
        signal={},
        trade_plan={},
        probability={},
        spot=24100.0,
    )

    render(dashboard)

    first = columns[0]
    assert first.warning_values == ["UNAVAILABLE"]
    assert ("Spot", "24100.00") in columns[4].metric_values
    assert ("Bullish %", "UNAVAILABLE%") in columns[6].metric_values
    assert ("Confidence", "UNAVAILABLE") in columns[7].metric_values
    assert ("Recommended", "UNAVAILABLE") in columns[8].metric_values
    assert ("Risk Reward", "UNAVAILABLE") in columns[8].metric_values
