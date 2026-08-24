import numpy as np
import pandas as pd

from analytics.liquidity.absorption_engine import AbsorptionEngine


def test_absorption_ignores_missing_quote_values_without_fabricating_signals():
    df = pd.DataFrame(
        [
            {
                "Strike": 24000,
                "CE_OI": None,
                "CE_VOLUME": None,
                "PE_OI": None,
                "PE_VOLUME": None,
            },
            {
                "Strike": 24050,
                "CE_OI": np.nan,
                "CE_VOLUME": np.nan,
                "PE_OI": np.nan,
                "PE_VOLUME": np.nan,
            },
        ]
    )

    result = AbsorptionEngine().analyze(df)

    assert result == {"count": 0, "levels": []}


def test_absorption_uses_only_valid_rows_for_each_option_side():
    df = pd.DataFrame(
        [
            {
                "Strike": 24000,
                "CE_OI": 100,
                "CE_VOLUME": 200,
                "PE_OI": None,
                "PE_VOLUME": None,
            },
            {
                "Strike": 24050,
                "CE_OI": 300,
                "CE_VOLUME": 100,
                "PE_OI": None,
                "PE_VOLUME": None,
            },
            {
                "Strike": 24100,
                "CE_OI": None,
                "CE_VOLUME": None,
                "PE_OI": 100,
                "PE_VOLUME": 200,
            },
            {
                "Strike": 24150,
                "CE_OI": None,
                "CE_VOLUME": None,
                "PE_OI": 300,
                "PE_VOLUME": 100,
            },
        ]
    )

    result = AbsorptionEngine().analyze(df)

    assert result["count"] == 4
    assert result["levels"] == [
        {"strike": 24000.0, "side": "CE", "type": "BUY_ABSORPTION"},
        {"strike": 24050.0, "side": "CE", "type": "SELL_ABSORPTION"},
        {"strike": 24100.0, "side": "PE", "type": "BUY_ABSORPTION"},
        {"strike": 24150.0, "side": "PE", "type": "SELL_ABSORPTION"},
    ]
