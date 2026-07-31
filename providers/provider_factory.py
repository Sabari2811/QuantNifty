from config.settings import PROVIDER

from providers.indmoney_provider import INDMoneyProvider
from providers.mock_provider import MockProvider


class ProviderFactory:

    @staticmethod
    def create(provider_name=None):

        if provider_name is None:
            provider_name = PROVIDER

        provider_name = provider_name.lower()

        if provider_name == "indmoney":

            provider = INDMoneyProvider()

        elif provider_name == "mock":

            provider = MockProvider()

        else:

            raise ValueError(
                f"Unsupported Provider : {provider_name}"
            )

        provider.connect()

        return provider