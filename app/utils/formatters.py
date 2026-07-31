"""
Global formatting helpers for QuantNifty.

All UI components should use these helpers instead of creating
their own formatting functions.

Author : QuantNifty
"""

from typing import Any


# ==========================================================
# Generic
# ==========================================================

def is_number(value: Any) -> bool:
    try:
        float(value)
        return True
    except Exception:
        return False


# ==========================================================
# Strike
# ==========================================================

def format_strike(value: Any) -> str:
    """
    23800.0 -> 23,800
    """

    if not is_number(value):
        return "-"

    return f"{int(float(value)):,}"


# ==========================================================
# Number
# ==========================================================

def format_number(value: Any, decimals: int = 0) -> str:
    """
    4312356 -> 4,312,356
    """

    if not is_number(value):
        return "-"

    return f"{float(value):,.{decimals}f}"


# ==========================================================
# Ratio
# ==========================================================

def format_ratio(value: Any) -> str:

    if not is_number(value):
        return "-"

    return f"{float(value):.2f}"


# ==========================================================
# Percent
# ==========================================================

def format_percent(value: Any, decimals: int = 0) -> str:

    if not is_number(value):
        return "-"

    return f"{float(value):.{decimals}f}%"


# ==========================================================
# Probability
# ==========================================================

def format_probability(value: Any) -> str:

    return format_percent(value, 0)


# ==========================================================
# IV
# ==========================================================

def format_iv(value: Any) -> str:
    """
    0.1434 -> 14.34%
    """

    if not is_number(value):
        return "-"

    return f"{float(value) * 100:.2f}%"


# ==========================================================
# Currency
# ==========================================================

def format_currency(value: Any) -> str:

    if not is_number(value):
        return "-"

    return f"₹{float(value):,.2f}"


# ==========================================================
# Points
# ==========================================================

def format_points(value: Any) -> str:

    if not is_number(value):
        return "-"

    return f"{float(value):,.2f} pts"


# ==========================================================
# GEX / DEX
# ==========================================================

def format_gex(value: Any) -> str:

    if not is_number(value):
        return "-"

    return f"{float(value):,.2f}"


# ==========================================================
# Large Numbers
# ==========================================================

def format_compact(value: Any) -> str:
    """
    1250000 -> 1.25M
    """

    if not is_number(value):
        return "-"

    value = float(value)

    if abs(value) >= 1_000_000_000:
        return f"{value/1_000_000_000:.2f}B"

    if abs(value) >= 1_000_000:
        return f"{value/1_000_000:.2f}M"

    if abs(value) >= 1_000:
        return f"{value/1_000:.2f}K"

    return f"{value:.2f}"