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

    column_groups = iter(
        [
            [Column() for _ in range(4)],
            [Column() for _ in range(4)],
            [Column() for _ in range(2)],
        ]
    )
    rendered_groups = []

    def columns(count):
        group = next(column_groups)
        assert len(group) == count
        rendered_groups.append(group)
        return group

    monkeypatch.setattr("dashboard.components.market_banner.st.columns", columns)
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

    first_group, second_group, third_group = rendered_groups
    assert first_group[0].warning_values == ["UNAVAILABLE"]
    assert ("Spot", "24100.00") in first_group[1].metric_values
    assert ("Bullish %", "UNAVAILABLE%") in second_group[2].metric_values
    assert ("Confidence", "UNAVAILABLE") in second_group[3].metric_values
    assert ("Recommended", "UNAVAILABLE") in third_group[0].metric_values
    assert ("Risk Reward", "UNAVAILABLE") in third_group[1].metric_values
