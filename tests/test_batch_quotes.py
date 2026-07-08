from providers.indmoney_provider import INDMoneyProvider

provider = INDMoneyProvider()
provider.connect()

security_ids = [
    44635,
    44639,
    44640,
    44641,
    44642,
    44643,
    44645,
    44646,
    44649,
    44651
]

for size in [6, 7, 8, 9, 10]:

    print("\n" + "=" * 60)
    print(f"Testing Batch Size : {size}")
    print("=" * 60)

    try:

        quotes = provider.get_quotes(security_ids[:size])

        print("SUCCESS")
        print("Returned :", len(quotes))

    except Exception as e:

        print("FAILED")
        print(e)