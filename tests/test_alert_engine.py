from types import SimpleNamespace

from monitoring.alert_engine import AlertEngine


def test_alert_engine_emits_runtime_failure_without_inventing_trade_state():
    dashboard = SimpleNamespace(cycle_no=7, runtime_status="FAILED", signal=None, dealer=None)
    events = AlertEngine().evaluate(dashboard)

    assert [(event.code, event.severity) for event in events] == [("RUNTIME_FAILURE", "CRITICAL")]


def test_alert_engine_emits_high_conviction_only_from_explicit_confidence():
    dashboard = SimpleNamespace(
        cycle_no=8,
        runtime_status="READY",
        signal={"confidence": 85},
        dealer=None,
    )
    events = AlertEngine().evaluate(dashboard)

    assert [event.code for event in events] == ["HIGH_CONVICTION"]


def test_alert_engine_emits_gamma_transition_from_two_explicit_states():
    previous = {"dealer": {"dealer_gamma": "LONG"}}
    dashboard = SimpleNamespace(
        cycle_no=9,
        runtime_status="READY",
        signal=None,
        dealer={"dealer_gamma": "SHORT"},
    )
    events = AlertEngine().evaluate(dashboard, previous=previous)

    assert [event.code for event in events] == ["GAMMA_REGIME_TRANSITION"]
    assert events[0].message == "LONG -> SHORT"


def test_alert_engine_does_not_treat_missing_confidence_as_high_conviction():
    dashboard = SimpleNamespace(
        cycle_no=10,
        runtime_status="READY",
        signal={},
        dealer=None,
    )

    assert AlertEngine().evaluate(dashboard) == []
