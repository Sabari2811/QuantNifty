from datetime import datetime

import pandas as pd

from tools.validate_live_expiry import validate


class _Manager:
    def __init__(self):
        self.downloaded = []

    def download_instruments(self, source):
        self.downloaded.append(source)

    def get_nearest_weekly_expiry(self, symbol):
        return "2026-09-03"

    def get_options(self, symbol):
        return pd.DataFrame(
            {
                "EXPIRY_DATE": ["2026-09-03", "2026-09-03"],
                "EXPIRY_FLAG": ["W", "W"],
            }
        )


def test_validate_refreshes_fno_and_requires_weekly_future(monkeypatch):
    manager = _Manager()
    monkeypatch.setattr("tools.validate_live_expiry.INDMoneyProvider", object, raising=False)
    monkeypatch.setattr("tools.validate_live_expiry.InstrumentManager", lambda: manager)
    monkeypatch.setattr("tools.validate_live_expiry.datetime", type("FixedDateTime", (), {
        "now": staticmethod(lambda: datetime(2026, 8, 30, 12, 0, 0)),
        "strptime": staticmethod(datetime.strptime),
    }))

    result = validate("NIFTY")

    assert manager.downloaded == ["fno"]
    assert result["expiry"] == "2026-09-03"
    assert result["expiry_flag"] == "W"
    assert result["master_refreshed"] is True


def test_validate_rejects_non_weekly_expiry(monkeypatch):
    class MonthlyManager(_Manager):
        def get_options(self, symbol):
            return pd.DataFrame({"EXPIRY_DATE": ["2026-09-03"], "EXPIRY_FLAG": ["M"]})

    manager = MonthlyManager()
    monkeypatch.setattr("tools.validate_live_expiry.InstrumentManager", lambda: manager)
    monkeypatch.setattr("tools.validate_live_expiry.datetime", type("FixedDateTime", (), {
        "now": staticmethod(lambda: datetime(2026, 8, 30, 12, 0, 0)),
        "strptime": staticmethod(datetime.strptime),
    }))

    try:
        validate("NIFTY")
    except RuntimeError as exc:
        assert "not marked weekly" in str(exc)
    else:
        raise AssertionError("monthly expiry must be rejected")
