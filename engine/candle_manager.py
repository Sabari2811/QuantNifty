import pandas as pd


class CandleManager:
    """
    Converts provider candle data into a standardized DataFrame.

    Standard Columns

        datetime
        open
        high
        low
        close
        volume
    """

    def to_dataframe(self, candles):

        if not candles:

            return pd.DataFrame(
                columns=[
                    "datetime",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume"
                ]
            )

        rows = []

        for candle in candles:

            rows.append({

                "datetime": pd.to_datetime(
                    candle["ts"],
                    unit="s"
                ),

                "open": float(candle["o"]),

                "high": float(candle["h"]),

                "low": float(candle["l"]),

                "close": float(candle["c"]),

                "volume": float(candle["v"])

            })

        df = pd.DataFrame(rows)

        df.sort_values(
            "datetime",
            inplace=True
        )

        df.reset_index(
            drop=True,
            inplace=True
        )

        return df