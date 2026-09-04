import pandas as pd
import pytest

from decision.models.option_contract import OptionContract
from execution.execution_contract import ExecutionAction, OrderIntent
from execution.instrument_execution_resolver import InstrumentExecutionResolver


class StubInstrumentManager:
    def __init__(self):
        self.option = {
            "SECURITY_ID": 123456,
            "LOT_UNITS": 65,
        }

    def get_security_id(self, symbol, expiry, strike, option_type):
        return int(self.option["SECURITY_ID"])

    def get_option(self, symbol, expiry, strike, option_type):
        return pd.Series(self.option)


def intent(expiry="2026-09-10"):
    return OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=24000,
        action=ExecutionAction.BUY,
        quantity=65,
        limit_price=100,
        metadata={"expiry": expiry},
    )


def test_resolver_returns_authoritative_security_id_and_lot_size():
    resolved = InstrumentExecutionResolver(StubInstrumentManager()).resolve(intent())

    assert resolved.security_id == 123456
    assert resolved.symbol == "NIFTY"
    assert resolved.expiry == "2026-09-10"
    assert resolved.strike == 24000
    assert resolved.option_type == "CE"
    assert resolved.lot_units == 65


def test_resolver_requires_expiry():
    order = intent()
    order = OrderIntent(
        symbol=order.symbol,
        option_type=order.option_type,
        strike=order.strike,
        action=order.action,
        quantity=order.quantity,
        limit_price=order.limit_price,
    )

    with pytest.raises(ValueError, match="expiry is required"):
        InstrumentExecutionResolver(StubInstrumentManager()).resolve(order)


def test_resolver_fails_when_contract_is_missing():
    class MissingManager(StubInstrumentManager):
        def get_security_id(self, *args):
            return None

    with pytest.raises(LookupError, match="No authoritative instrument"):
        InstrumentExecutionResolver(MissingManager()).resolve(intent())


def test_resolver_rejects_security_id_disagreement():
    class ChangingManager(StubInstrumentManager):
        def get_option(self, *args):
            return pd.Series({"SECURITY_ID": 999999, "LOT_UNITS": 65})

    with pytest.raises(ValueError, match="security ID changed"):
        InstrumentExecutionResolver(ChangingManager()).resolve(intent())
