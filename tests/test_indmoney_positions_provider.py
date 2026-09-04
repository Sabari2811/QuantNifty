from unittest.mock import Mock, patch

import pytest

from providers.indmoney_provider import INDMoneyProvider


@pytest.fixture
def provider(monkeypatch):
    monkeypatch.setenv("INDSTOCKS_API_TOKEN", "test-token")
    return INDMoneyProvider()


def test_get_positions_returns_documented_derivative_payload(provider):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "status": "success",
        "data": [
            {
                "position_id": "535654528",
                "security_id": "823580",
                "symbol": "NIFTY",
                "segment": "DERIVATIVE",
                "product": "MARGIN",
                "drv_instrument": "OPTIDX",
                "drv_option_type": "CE",
                "drv_strike_price": 25000,
                "net_qty": 75,
                "avg_price": 120.5,
            }
        ],
    }

    with patch("providers.indmoney_provider.requests.get", return_value=response) as get:
        result = provider.get_positions()

    assert result[0]["position_id"] == "535654528"
    assert result[0]["net_qty"] == 75
    get.assert_called_once_with(
        "https://api.indstocks.com/portfolio/positions",
        headers=provider.headers,
        params={"segment": "derivative", "product": "margin"},
        timeout=30,
    )


def test_get_positions_does_not_relabel_provider_position_id(provider):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "status": "success",
        "data": [{"position_id": "POS-1", "security_id": "123", "net_qty": 75}],
    }

    with patch("providers.indmoney_provider.requests.get", return_value=response):
        result = provider.get_positions()

    assert result[0]["position_id"] == "POS-1"
    assert "client_order_id" not in result[0]


def test_get_positions_rejects_invalid_segment(provider):
    with pytest.raises(ValueError, match="Unsupported positions segment"):
        provider.get_positions(segment="bad", product="margin")


def test_get_positions_fails_closed_on_http_error(provider):
    response = Mock()
    response.raise_for_status.side_effect = Exception("http failure")

    with patch("providers.indmoney_provider.requests.get", return_value=response):
        with pytest.raises(Exception, match="http failure"):
            provider.get_positions()
