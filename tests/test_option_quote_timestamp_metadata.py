from datetime import datetime, timezone

import pandas as pd

from engine.market_data_pipeline import MarketDataPipeline


def test_attach_option_quote_timestamps_preserves_security_id_metadata():
    chain = pd.DataFrame(
        [
            {
                "Strike": 24150,
                "CE_ID": 42645,
                "PE_ID": 42646,
                "CE_LTP": 38.9,
                "PE_LTP": 188.5,
            }
        ]
    )
    timestamp = datetime(2026, 9, 4, 5, 4, 58, tzinfo=timezone.utc)

    result = MarketDataPipeline.attach_option_quote_timestamps(
        chain,
        {42645: timestamp, 42646: timestamp},
    )

    assert result is chain
    assert result.attrs["option_quote_timestamps"] == {
        "42645": timestamp,
        "42646": timestamp,
    }


def test_attach_option_quote_timestamps_omits_missing_values():
    chain = pd.DataFrame(
        [{"Strike": 24200, "CE_ID": 42647, "PE_ID": 42648}]
    )

    MarketDataPipeline.attach_option_quote_timestamps(
        chain,
        {42647: None, 42648: datetime(2026, 9, 4, 5, 4, 58, tzinfo=timezone.utc)},
    )

    assert result := chain.attrs["option_quote_timestamps"]
    assert "42647" not in result
    assert result["42648"].year == 2026
