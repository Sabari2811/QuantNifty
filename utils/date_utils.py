from datetime import datetime
import pandas as pd


class DateUtils:

    @staticmethod
    def parse(value):
        """
        Converts any supported date format into pandas.Timestamp.
        """

        if value is None:
            return None

        if isinstance(value, pd.Timestamp):
            return value

        try:
            return pd.to_datetime(value)
        except Exception:
            return None

    @staticmethod
    def normalize(value):
        """
        Returns normalized timestamp.
        """

        ts = DateUtils.parse(value)

        if ts is None:
            return None

        return ts.normalize()

    @staticmethod
    def equal(a, b):

        a = DateUtils.normalize(a)
        b = DateUtils.normalize(b)

        if a is None or b is None:
            return False

        return a == b