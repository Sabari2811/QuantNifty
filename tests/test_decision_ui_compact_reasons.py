from app.components.ai_decision_card import _compact_reasons


def test_compact_reasons_deduplicates_and_limits_output():
    reasons = [
        "Dealers Long Gamma",
        "Positive Delta",
        "Positive Vanna",
        "Dealers Long Gamma",
        "Gamma Flip",
    ]

    assert _compact_reasons(reasons) == [
        "Long Gamma",
        "Positive Delta",
        "Positive Vanna",
    ]


def test_compact_reasons_handles_empty_input():
    assert _compact_reasons([]) == []


def test_compact_reasons_preserves_unknown_reason_text():
    assert _compact_reasons(["Custom Signal"])[0] == "Custom Signal"
