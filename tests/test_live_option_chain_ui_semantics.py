import numpy as np
import pandas as pd

from app.components.live_option_chain import (
    _display_series,
    _format_missing,
    _provenance_message,
)


def test_display_series_preserves_zero_and_renders_missing_as_dash():
    values = pd.Series([0.0, np.nan, 12.5])

    result = _display_series(values, 2)

    assert result.iloc[0] == "0.00"
    assert result.iloc[1] == "—"
    assert result.iloc[2] == "12.50"


def test_display_series_formats_integer_like_values_without_decimal_noise():
    values = pd.Series([5939365.0, 0.0, np.nan])

    result = _display_series(values)

    assert result.iloc[0] == "5939365"
    assert result.iloc[1] == "0"
    assert result.iloc[2] == "—"


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
