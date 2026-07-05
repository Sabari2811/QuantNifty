from providers.indmoney_provider import INDMoneyProvider

provider = INDMoneyProvider()

provider.connect()

print("\nFetching User Profile...\n")

response = provider.get_profile()

print(response)