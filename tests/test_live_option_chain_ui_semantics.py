import numpy as np
import pandas as pd

from app.components.live_option_chain import _display_series, _provenance_message


def test_display_series_preserves_real_zero_and_marks_missing():
    values = pd.Series([0.0, np.nan, 12.5])

    result = _display_series(values, 2)

    assert result.iloc[0] == 0.0
    assert result.iloc[1] == "—"
    assert result.iloc[2] == 12.5


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
