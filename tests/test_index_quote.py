from providers.indmoney_provider import INDMoneyProvider

provider = INDMoneyProvider()
provider.connect()

quote = provider.get_index_quote("NIFTY 50")

print()
print("=" * 60)
print("LIVE NIFTY QUOTE")
print("=" * 60)

print(quote)