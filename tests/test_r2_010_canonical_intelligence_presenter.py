def test_dashboard_uses_canonical_intelligence_presenter():
    from pathlib import Path

    source = Path("app/pages/dashboard.py").read_text(encoding="utf-8")

    assert "from dashboard.components.intelligence_card import render as intelligence" in source
    assert "from dashboard.intelligence_adapter import adapt_intelligence" in source
    assert "intelligence(adapt_intelligence(ctx.intelligence))" in source
    assert "from app.components.intelligence_card import show as intelligence" not in source
