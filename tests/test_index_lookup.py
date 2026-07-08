from engine.instrument_manager import InstrumentManager

im = InstrumentManager()

df = im.load_index()

targets = [
    "NIFTY 50",
    "NIFTY BANK",
    "NIFTY FIN SERVICE",
    "NIFTY MID SELECT"
]

for target in targets:

    print("\n" + "=" * 60)
    print(target)
    print("=" * 60)

    result = df[
        df["SEGMENT"]
        .astype(str)
        .str.upper()
        .str.contains(target.upper(), na=False)
    ]

    if result.empty:
        print("Not Found")
    else:
        print(result)