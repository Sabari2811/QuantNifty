"""
Status badge helpers.
"""


def dealer_gamma(value):

    mapping = {
        "LONG": "🟢 LONG",
        "SHORT": "🔴 SHORT"
    }

    return mapping.get(str(value).upper(), str(value))


def market_mode(value):

    mapping = {
        "PINNED": "🟡 PINNED",
        "TRENDING": "🔵 TRENDING"
    }

    return mapping.get(str(value).upper(), str(value))


def pressure(value):

    mapping = {
        "BUY": "🟢 BUY",
        "SELL": "🔴 SELL",
        "NEUTRAL": "⚪ NEUTRAL"
    }

    return mapping.get(str(value).upper(), str(value))


def volatility(value):

    mapping = {
        "LOW": "🟢 LOW",
        "NORMAL": "🟡 NORMAL",
        "HIGH": "🔴 HIGH"
    }

    return mapping.get(str(value).upper(), str(value))


def signal(value):

    mapping = {
        "BUY CALL": "🟢 BUY CALL",
        "BUY PUT": "🔴 BUY PUT",
        "WAIT": "🟡 WAIT",
        "NO TRADE": "⚪ NO TRADE"
    }

    return mapping.get(str(value).upper(), str(value))