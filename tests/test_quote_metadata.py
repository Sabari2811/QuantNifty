from datetime import datetime, timezone

from core.quote_metadata import extract_provider_timestamp, parse_provider_timestamp


def test_parse_provider_timestamp_handles_iso_zulu():
    value = parse_provider_timestamp("2026-08-30T07:16:17Z")
    assert value == datetime(2026, 8, 30, 7, 16, 17, tzinfo=timezone.utc)


def test_parse_provider_timestamp_rejects_invalid_values():
    assert parse_provider_timestamp("not-a-timestamp") is None
    assert parse_provider_timestamp(None) is None


def test_extract_provider_timestamp_prefers_normalized_value():
    value = extract_provider_timestamp({
        "provider_timestamp": "2026-08-30T07:16:17Z",
        "timestamp": "2026-08-30T07:16:18Z",
    })
    assert value == datetime(2026, 8, 30, 7, 16, 17, tzinfo=timezone.utc)


def test_extract_provider_timestamp_accepts_provider_alias():
    value = extract_provider_timestamp({"exchangeTimestamp": "2026-08-30T07:16:17+00:00"})
    assert value == datetime(2026, 8, 30, 7, 16, 17, tzinfo=timezone.utc)


def test_extract_provider_timestamp_returns_none_when_absent():
    assert extract_provider_timestamp({"live_price": 100.0}) is None
