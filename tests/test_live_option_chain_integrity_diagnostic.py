import pandas as pd

from tools.inspect_live_option_chain_integrity import _contract_diagnostics


def test_contract_diagnostic_reports_intrinsic_shortfall_and_identity():
    chain = pd.DataFrame([
        {
            "Strike": 24900,
            "CE_ID": 111,
            "CE_LTP": 120,
            "CE_OI": 45000,
            "CE_VOLUME": 1200,
            "PE_ID": 222,
            "PE_LTP": 80,
            "PE_OI": 43000,
            "PE_VOLUME": 900,
        }
    ])

    result = _contract_diagnostics(
        chain,
        25050,
        (("strike:24900|CE:111|PE:222|row:0", ("ce_ltp_below_intrinsic",)),),
    )

    assert result[0]["contract"] == "strike:24900|CE:111|PE:222|row:0"
    assert result[0]["ce"]["ltp"] == 120.0
    assert result[0]["ce"]["intrinsic"] == 150.0
    assert result[0]["ce"]["shortfall_below_intrinsic"] == 30.0
    assert result[0]["pe"]["intrinsic"] == 0.0


def test_contract_diagnostic_preserves_findings_when_row_is_unavailable():
    result = _contract_diagnostics(
        pd.DataFrame(),
        25050,
        (("strike:24900|CE:111|PE:222|row:0", ("ce_ltp_below_intrinsic",)),),
    )

    assert result == [
        {
            "contract": "strike:24900|CE:111|PE:222|row:0",
            "reasons": ["ce_ltp_below_intrinsic"],
        }
    ]
