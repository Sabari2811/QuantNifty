import numpy as np
import pandas as pd

from app.components.live_option_chain import (
    _display_series,
    _format_missing,
    _format_series_value,
    _provenance_message,
)


def test_display_series_preserves_numeric_values_and_missing_as_na():
    values = pd.Series([0.0, np.nan, 12.5])

    result = _display_series(values, 2)

    assert pd.api.types.is_numeric_dtype(result)
    assert result.iloc[0] == 0.0
    assert pd.isna(result.iloc[1])
    assert result.iloc[2] == 12.5


def test_format_series_value_renders_precision_and_missing_values():
    assert _format_series_value(0.0, 2) == "0.00"
    assert _format_series_value(np.nan, 2) == "—"
    assert _format_series_value(12.5, 2) == "12.50"


def test_format_series_value_avoids_integer_decimal_noise():
    assert _format_series_value(5939365.0) == "5939365"
    assert _format_series_value(0.0) == "0"
    assert _format_series_value(np.nan) == "—"


def test_missing_value_formatter_shows_dash_and_preserves_zero():
    assert _format_missing(np.nan) == "—"
    assert _format_missing(None) == "—"
    assert _format_missing(0.0) == 0.0
    assert _format_missing(12.5) == 12.5


def test_provenance_message_identifies_incomplete_acquisition():
    class Acquisition:
        complete = False

    class Provenance:
        option_chain = Acquisition()
        spot = None
        candles = None

    class Context:
        data_provenance = Provenance()

    message = _provenance_message(Context())

    assert message is not None
    assert "option chain" in message
    assert "Missing observations are shown as —" in message


def test_provenance_message_is_absent_when_acquisition_is_complete():
    class Acquisition:
        complete = True

    class Provenance:
        option_chain = Acquisition()
        spot = Acquisition()
        candles = Acquisition()

    class Context:
        data_provenance = Provenance()

    assert _provenance_message(Context()) is None
