from __future__ import annotations

from datetime import datetime, timezone


def parse_provider_timestamp(value):
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def extract_provider_timestamp(quote: dict | None):
    if not isinstance(quote, dict):
        return None
    for key in (
        "provider_timestamp",
        "quote_timestamp",
        "timestamp",
        "exchange_timestamp",
        "exchangeTimestamp",
        "last_trade_time",
        "lastTradeTime",
        "updated_at",
        "updatedAt",
        "time",
    ):
        parsed = parse_provider_timestamp(quote.get(key))
        if parsed is not None:
            return parsed
    return None
