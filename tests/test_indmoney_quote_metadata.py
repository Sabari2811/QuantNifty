from providers.indmoney_provider import INDMoneyProvider


def test_quote_metadata_preserves_provider_timestamp_and_bid_ask(monkeypatch):
    quote = {
        "live_price": 100.0,
        "timestamp": "2026-08-26T06:00:00Z",
        "bidPrice": 99.5,
        "askPrice": 100.5,
    }

    result = INDMoneyProvider._normalise_quote(quote)

    assert result["provider_timestamp"] == quote["timestamp"]
    assert result["bid_price"] == 99.5
    assert result["ask_price"] == 100.5
    assert result["live_price"] == 100.0


def test_quote_metadata_does_not_fabricate_missing_timestamp_or_prices():
    quote = {"live_price": 100.0}

    result = INDMoneyProvider._normalise_quote(quote)

    assert "provider_timestamp" not in result
    assert "bid_price" not in result
    assert "ask_price" not in result
    assert result["live_price"] == 100.0


def test_quote_metadata_does_not_mutate_provider_payload():
    quote = {"live_price": 100.0, "timestamp": "2026-08-26T06:00:00Z"}
    original = dict(quote)

    result = INDMoneyProvider._normalise_quote(quote)

    assert quote == original
    assert result is not quote
