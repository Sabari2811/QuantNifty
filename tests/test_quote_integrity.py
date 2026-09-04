import pandas as pd

from core.quote_integrity import assess_option_chain


def _chain(**overrides):
    row = {
        "Strike": 25000,
        "CE_ID": 111,
        "CE_LTP": 150,
        "CE_OI": 45000,
        "CE_VOLUME": 1200,
        "PE_ID": 222,
        "PE_LTP": 140,
        "PE_OI": 43000,
        "PE_VOLUME": 900,
    }
    row.update(overrides)
    return pd.DataFrame([row])


def test_valid_option_chain_is_valid():
    report = assess_option_chain(_chain(), spot_price=25050)

    assert report.status == "VALID"
    assert report.usable_for_analytics is True
    assert report.checked_contracts == 1
    assert report.valid_contracts == 1
    assert report.suspect_contracts == 0
    assert report.invalid_contracts == 0


def test_below_intrinsic_ltp_is_suspect_not_invalid():
    report = assess_option_chain(
        _chain(Strike=24900, CE_LTP=120),
        spot_price=25050,
    )

    assert report.status == "SUSPECT"
    assert report.usable_for_analytics is True
    assert report.suspect_contracts == 1
    assert report.invalid_contracts == 0
    assert "ce_ltp_below_intrinsic" in report.reasons


def test_integrity_finding_preserves_contract_identity():
    report = assess_option_chain(
        _chain(Strike=24900, CE_LTP=120),
        spot_price=25050,
    )

    assert report.contract_reasons == (
        (
            "strike:24900|CE:111|PE:222|row:0",
            ("ce_ltp_below_intrinsic",),
        ),
    )


def test_integrity_finding_normalizes_pandas_float_contract_ids():
    report = assess_option_chain(
        _chain(
            Strike=24900,
            CE_ID=111.0,
            CE_LTP=120,
            PE_ID=222.0,
        ),
        spot_price=25050,
    )

    assert report.contract_reasons[0][0] == (
        "strike:24900|CE:111|PE:222|row:0"
    )


def test_negative_ltp_is_invalid():
    report = assess_option_chain(
        _chain(CE_LTP=-1),
        spot_price=25050,
    )

    assert report.status == "INVALID"
    assert report.usable_for_analytics is False
    assert report.invalid_contracts == 1
    assert "negative_ce_ltp" in report.reasons


def test_missing_ltp_is_invalid():
    report = assess_option_chain(
        _chain(CE_LTP=None),
        spot_price=25050,
    )

    assert report.status == "INVALID"
    assert report.invalid_contracts == 1
    assert "missing_ce_ltp" in report.reasons


def test_negative_open_interest_is_invalid():
    report = assess_option_chain(
        _chain(PE_OI=-1),
        spot_price=25050,
    )

    assert report.status == "INVALID"
    assert "negative_pe_oi" in report.reasons


def test_invalid_spot_is_invalid_without_mutating_chain():
    chain = _chain()
    before = chain.copy(deep=True)

    report = assess_option_chain(chain, spot_price=None)

    assert report.status == "INVALID"
    assert report.invalid_contracts == 1
    pd.testing.assert_frame_equal(chain, before)


def test_report_serializes_without_losing_contract_reasons():
    report = assess_option_chain(
        _chain(Strike=24900, CE_LTP=120),
        spot_price=25050,
    )

    payload = report.as_dict()

    assert payload["status"] == "SUSPECT"
    assert payload["contract_reasons"]
    assert payload["contract_reasons"][0][0] == (
        "strike:24900|CE:111|PE:222|row:0"
    )
    assert payload["contract_reasons"][0][1] == (
        "ce_ltp_below_intrinsic",
    )
