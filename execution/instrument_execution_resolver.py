from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExecutionInstrument:
    """Authoritative tradable-contract identity resolved from the instrument master."""

    security_id: int
    symbol: str
    expiry: str
    strike: float
    option_type: str
    lot_units: int


class InstrumentExecutionResolver:
    """Resolve a canonical OrderIntent to a provider security ID.

    Resolution is deliberately read-only: it never downloads instruments,
    synthesizes IDs, or falls back to a different expiry/contract.
    """

    def __init__(self, instrument_manager):
        self.instrument_manager = instrument_manager

    def resolve(self, intent):
        if intent is None:
            raise ValueError("Order intent is required")

        expiry = str(getattr(intent, "metadata", {}).get("expiry", "") or "").strip()
        if not expiry:
            raise ValueError("Order intent expiry is required for instrument resolution")

        security_id = self.instrument_manager.get_security_id(
            intent.symbol,
            expiry,
            intent.strike,
            intent.option_type,
        )
        if security_id is None:
            raise LookupError(
                "No authoritative instrument found for "
                f"{intent.symbol} {expiry} {intent.strike} {intent.option_type}"
            )

        option = self.instrument_manager.get_option(
            intent.symbol,
            expiry,
            intent.strike,
            intent.option_type,
        )
        if option is None:
            raise LookupError("Instrument disappeared during resolution")

        resolved_security_id = int(option["SECURITY_ID"])
        if resolved_security_id != int(security_id):
            raise ValueError("Instrument security ID changed during resolution")

        return ExecutionInstrument(
            security_id=resolved_security_id,
            symbol=str(intent.symbol),
            expiry=expiry,
            strike=float(intent.strike),
            option_type=str(intent.option_type).upper(),
            lot_units=int(option["LOT_UNITS"]),
        )
