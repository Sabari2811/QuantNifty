from pathlib import Path


APP = Path(__file__).parents[1] / "dashboard" / "app.py"
COCKPIT = Path(__file__).parents[1] / "dashboard" / "components" / "trade_cockpit.py"


def test_live_monitor_is_owned_by_primary_cockpit_only():
    app = APP.read_text(encoding="utf-8")
    cockpit = COCKPIT.read_text(encoding="utf-8")

    assert "render_live_trade_monitor" not in app
    assert "render_live_trade_monitor(dashboard)" in cockpit
    assert app.count("render_trade_cockpit(dashboard)") == 1


def test_existing_terminal_sections_remain_present():
    app = APP.read_text(encoding="utf-8")
    for marker in (
        "market_banner.render(dashboard)",
        "market_regime.render(dashboard)",
        "liquidity_card.render(dashboard.liquidity)",
        "trade_plan.render(dashboard.trade_plan, decision)",
        "risk_card.render(dashboard.risk)",
        "option_chain.render(",
        "greeks_table.render(dashboard.greeks)",
        "render_execution_state(ui_contract[\"sections\"])",
        "render_brain_performance(dashboard)",
        "render_backend_ui_integrity(integrity_report)",
    ):
        assert marker in app
