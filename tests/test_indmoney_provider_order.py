from unittest.mock import Mock, patch

import pytest
import requests

from providers.indmoney_provider import INDMoneyProvider


@pytest.fixture
def provider(monkeypatch):
    monkeypatch.setenv("INDSTOCKS_API_TOKEN", "test-token")
    return INDMoneyProvider()


def order_request():
    return {
        "txn_type": "BUY",
        "exchange": "NSE",
        "segment": "DERIVATIVE",
        "product": "MARGIN",
        "order_type": "LIMIT",
        "validity": "DAY",
        "security_id": "823580",
        "qty": 75,
        "algo_id": "99999",
        "limit_price": 120.5,
        "is_amo": False,
        "remarks": "qn-test-order",
    }


def response(payload, status_code=200):
    result = Mock()
    result.status_code = status_code
    result.raise_for_status.return_value = None
    result.json.return_value = payload
    return result


def test_place_order_posts_exact_provider_payload(provider):
    payload = order_request()
    result = response({
        "status": "success",
        "data": {"order_id": "ORD-1", "order_status": "QUEUED"},
    })

    with patch("providers.indmoney_provider.requests.post", return_value=result) as post:
        actual = provider.place_order(payload)

    assert actual["status"] == "success"
    post.assert_called_once_with(
        "https://api.indstocks.com/order",
        headers=provider.headers,
        json=payload,
        timeout=30,
    )


def test_place_order_accepts_request_object(provider):
    request = Mock()
    request.as_dict.return_value = order_request()
    result = response({"status": "success", "data": {"order_id": "ORD-2"}})

    with patch("providers.indmoney_provider.requests.post", return_value=result) as post:
        actual = provider.place_order(request)

    assert actual["data"]["order_id"] == "ORD-2"
    assert post.call_args.kwargs["json"] == request.as_dict.return_value


def test_place_order_requires_request(provider):
    with pytest.raises(ValueError, match="Order request is required"):
        provider.place_order(None)


def test_place_order_requires_provider_fields(provider):
    payload = order_request()
    del payload["security_id"]

    with pytest.raises(ValueError, match="Missing provider order fields: security_id"):
        provider.place_order(payload)


def test_place_order_propagates_http_failure(provider):
    error = requests.HTTPError("http failure")
    result = Mock()
    result.raise_for_status.side_effect = error

    with patch("providers.indmoney_provider.requests.post", return_value=result):
        with pytest.raises(requests.HTTPError, match="http failure"):
            provider.place_order(order_request())


def test_place_order_rejects_invalid_json(provider):
    result = Mock()
    result.raise_for_status.return_value = None
    result.json.side_effect = ValueError("bad json")

    with patch("providers.indmoney_provider.requests.post", return_value=result):
        with pytest.raises(ValueError, match="invalid JSON"):
            provider.place_order(order_request())


def test_place_order_rejects_non_object_response(provider):
    result = response(["unexpected"])

    with patch("providers.indmoney_provider.requests.post", return_value=result):
        with pytest.raises(ValueError, match="invalid response"):
            provider.place_order(order_request())
