from dashboard.components.intelligence_card import _compact_provenance_reasons


def test_compact_provenance_reasons_are_human_readable_and_deduplicated():
    reasons = [
        "freshness_unverified:INDMoney index quote",
        "provider_quote_timestamp_unavailable",
        "integrity_suspect:INDMoney option quotes",
        "ce_ltp_below_intrinsic",
        "integrity_suspect:INDMoney option quotes",
    ]

    assert _compact_provenance_reasons(reasons) == [
        "Index quote freshness unverified",
        "Quote timestamp unavailable",
        "Option quote integrity suspect",
        "CE LTP below intrinsic value",
    ]


def test_compact_provenance_reasons_preserves_unknown_details():
    assert _compact_provenance_reasons(["custom_provenance_reason"]) == [
        "custom_provenance_reason"
    ]


def test_compact_provenance_reasons_handles_empty_input():
    assert _compact_provenance_reasons([]) == []
