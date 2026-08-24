import numpy as np
import pandas as pd

from app.components.live_option_chain import _display_series


def test_display_series_preserves_missing_numeric_values_as_na():
    series = pd.Series([1.23456, np.nan, 0.0], dtype="float64")

    result = _display_series(series, 4)

    assert pd.api.types.is_numeric_dtype(result)
    assert result.iloc[0] == 1.2346
    assert pd.isna(result.iloc[1])
    assert result.iloc[2] == 0.0


def test_display_series_does_not_replace_missing_values_with_text():
    series = pd.Series([10.0, np.nan], dtype="float64")

    result = _display_series(series)

    assert result.dtype.kind in "fc"
    assert pd.isna(result.iloc[1])
    assert "—" not in result.astype(str).tolist()
