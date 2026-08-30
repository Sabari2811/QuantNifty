from __future__ import annotations

from datetime import datetime, timezone
import math


def parse_provider_timestamp(value):
    """Parse provider timestamps without inventing missing timestamps.

    INDMoney may expose timestamps as ISO-8601 strings or epoch seconds/
    milliseconds. Numeric epoch values are normalized to UTC so freshness
    validation can use the provider's actual observation time.
    """
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)

    if isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        if not math.isfinite(float(value)):
            return None
        epoch = float(value)
        if epoch > 1_000_000_000_000:
            epoch /= 1000.0
        elif epoch > 1_000_000_000_000_000:
            epoch /= 1_000_000.0
        try:
            return datetime.fromtimestamp(epoch, tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None

    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            try:
                return parse_provider_timestamp(float(text))
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
