import requests


# Existing provider imports/classes remain unchanged above this section.

    # ==========================================================
    # INDEX QUOTE BY SECURITY ID
    # ==========================================================

    def get_index_quote_by_id(
        self,
        security_id
    ):

        security_id = int(
            security_id
        )

        url = (
            f"{self.base_url}/market/quotes/full"
            f"?scrip-codes=NIDX_{security_id}"
        )

        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error(
                "INDEX QUOTE REQUEST FAILED | security_id=%s | error=%s",
                security_id,
                exc,
            )
            return None

        try:
            data = response.json()
        except ValueError:
            logger.error(
                "INDEX QUOTE RESPONSE INVALID JSON | security_id=%s",
                security_id,
            )
            return None

        if data.get("status") != "success":
            logger.error(
                "INDEX QUOTE RESPONSE FAILED | security_id=%s | status=%s",
                security_id,
                data.get("status"),
            )
            return None

        return data.get("data", {}).get(
            f"NIDX_{security_id}"
        )

    # ==========================================================
    # INDEX QUOTE
    # ==========================================================

    def get_index_quote(
        self,
        index_name
    ):

        from engine.instrument_manager import (
            InstrumentManager
        )

        instrument = InstrumentManager()

        security_id = (
            instrument.get_index_security_id(
                index_name
            )
        )

        if security_id is None:

            raise ValueError(
                f"Index not found : {index_name}"
            )

        return self.get_index_quote_by_id(
            security_id
        )

    # ==========================================================
    # EXTRACT PRICE
    # ==========================================================

    def _extract_price(
        self,
        quote
    ):

        if quote is None:

            return None

        for key in (
            "live_price",
            "ltp",
            "LTP",
            "last_price",
            "lastPrice",
            "close",
        ):

            value = quote.get(
                key
