import pandas as pd

from engine.live_greeks_engine import LiveGreeksEngine


def test_live_greeks_preserves_chain_and_marks_invalid_contract_missing():
    option_chain = pd.DataFrame(
        [
            {
                "Strike": 25000,
                "CE_ID": 111,
                "CE_LTP": 150,
                "CE_OI": 45000,
                "CE_VOLUME": 1200,
                "PE_ID": 222,
                "PE_LTP": 140,
                "PE_OI": 43000,
                "PE_VOLUME": 900,
            },
            {
                "Strike": 25100,
                "CE_ID": 333,
                "CE_LTP": None,
                "CE_OI": 39000,
                "CE_VOLUME": 950,
                "PE_ID": 444,
                "PE_LTP": 165,
                "PE_OI": 47000,
                "PE_VOLUME": 1300,
            },
        ]
    )

    result = LiveGreeksEngine().calculate_chain_greeks(
        option_chain=option_chain,
        spot_price=25050,
        expiry="31/12/2026 15:30",
    )

    assert len(result) == len(option_chain)
    assert result.loc[1, "CE_IV"] is None
    assert result.loc[1, "CE_DELTA"] is None
    assert pd.notna(result.loc[0, "CE_IV"])
    assert pd.notna(result.loc[0, "PE_IV"])


def test_live_greeks_does_not_mutate_input():
    option_chain = pd.DataFrame(
        [{
            "Strike": 25000,
            "CE_LTP": 150,
            "CE_OI": 45000,
            "CE_VOLUME": 1200,
            "PE_LTP": 140,
            "PE_OI": 43000,
            "PE_VOLUME": 900,
        }]
    )
    original = option_chain.copy(deep=True)

    LiveGreeksEngine().calculate_chain_greeks(
        option_chain=option_chain,
        spot_price=25050,
        expiry="31/12/2026 15:30",
    )

    pd.testing.assert_frame_equal(option_chain, original)
