from engine.instrument_manager import InstrumentManager

manager = InstrumentManager()

for symbol in ["NIFTY", "BANKNIFTY", "MIDCPNIFTY"]:

    print("\n" + "=" * 70)
    print(symbol)
    print("=" * 70)

    df = manager.get_options(symbol)

    print(
        df[
            [
                "TRADING_SYMBOL",
                "EXPIRY_DATE",
                "EXPIRY_FLAG",
                "OPTION_TYPE"
            ]
        ]
        .sort_values("EXPIRY_DATE")
        .head(20)
    )