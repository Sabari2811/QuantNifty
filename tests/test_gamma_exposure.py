gex = GammaExposureEngine()

df = gex.calculate(df, spot)

print(df[
    [
        "Strike",
        "CE_GEX",
        "PE_GEX",
        "NET_GEX"
    ]
])

print(gex.total_gex(df))