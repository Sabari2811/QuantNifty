from config.settings import PROVIDER

from providers.mock_provider import MockProvider
from providers.indmoney_provider import INDMoneyProvider


class ProviderManager:
    """
    Chooses the active market data provider.
    """

    def __init__(self):

        provider = PROVIDER.lower()

        if provider == "mock":

            print("=" * 60)
            print(" USING MOCK PROVIDER ")
            print("=" * 60)

            self.provider = MockProvider()

        elif provider == "indmoney":

            print("=" * 60)
            print(" USING INDMONEY PROVIDER ")
            print("=" * 60)

            self.provider = INDMoneyProvider()

        else:

            raise ValueError(
                f"Unknown provider : {PROVIDER}"
            )

        self.provider.connect()

    def get_provider(self):

        return self.provider