from engine.instrument_manager import InstrumentManager

manager = InstrumentManager()

df = manager.get_dataframe("fno")

print(df[["TRADING_SYMBOL", "SYMBOL_NAME"]].head(50))