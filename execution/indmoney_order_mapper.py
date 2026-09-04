from __future__ import annotations

from dataclasses import dataclass

from execution.execution_contract import ExecutionAction, OrderIntent
from execution.instrument_execution_resolver import ExecutionInstrument


@dataclass(frozen=True, slots=True)
class INDMoneyOrderRequest:
    """Provider request payload for a standard NSE derivative order.

    This is a pure mapping boundary. It performs no network I/O and never
    creates or alters a provider instrument identity.
    """

    txn_type: str
    exchange: str
    segment: str
    product: str
    order_type: str
    validity: str
    security_id: str
    qty: int
    algo_id: str
    limit_price: float
    is_amo: bool
    remarks: str

    def as_dict(self) -> dict[str, object]:
        return {
            "txn_type": self.txn_type,
            "exchange": self.exchange,
            "segment": self.segment,
            "product": self.product,
            "order_type": self.order_type,
            "validity": self.validity,
            "security_id": self.security_id,
            "qty": self.qty,
            "algo_id": self.algo_id,
            "limit_price": self.limit_price,
            "is_amo": self.is_amo,
            "remarks": self.remarks,
        }


def build_indmoney_order_request(
    intent: OrderIntent,
    instrument: ExecutionInstrument,
    *,
    exchange: str = "NSE",
    segment: str = "DERIVATIVE",
    product: str = "MARGIN",
    order_type: str = "LIMIT",
    validity: str = "DAY",
    algo_id: str = "99999",
    is_amo: bool = False,
) -> INDMoneyOrderRequest:
    """Map canonical intent + resolved instrument to an INDMoney request.

    Provider-facing constants are restricted to documented NSE derivative
    standard-order values. No live request is made here.
    """
    if intent is None:
        raise ValueError("Order intent is required")
    if instrument is None:
        raise ValueError("Resolved execution instrument is required")

    if intent.action not in {ExecutionAction.BUY, ExecutionAction.SELL}:
        raise ValueError(f"Unsupported execution action: {intent.action}")
    if int(intent.quantity) <= 0:
        raise ValueError("Order quantity must be positive")
    if float(intent.limit_price) <= 0:
        raise ValueError("Limit price must be positive")
    if not str(intent.client_order_id).strip():
        raise ValueError("client_order_id is required for provider order mapping")
    if int(instrument.security_id) <= 0:
        raise ValueError("Resolved security_id must be positive")
    if int(instrument.lot_units) <= 0:
        raise ValueError("Resolved lot_units must be positive")
    if int(intent.quantity) % int(instrument.lot_units) != 0:
        raise ValueError("Order quantity must be a multiple of the resolved lot size")

    exchange = str(exchange).upper().strip()
    segment = str(segment).upper().strip()
    product = str(product).upper().strip()
    order_type = str(order_type).upper().strip()
    validity = str(validity).upper().strip()
    algo_id = str(algo_id).strip()

    if exchange != "NSE":
        raise ValueError("This mapper currently supports NSE only")
    if segment != "DERIVATIVE":
        raise ValueError("This mapper currently supports DERIVATIVE only")
    if product not in {"MARGIN", "INTRADAY"}:
        raise ValueError("Derivative product must be MARGIN or INTRADAY")
    if order_type != "LIMIT":
        raise ValueError("This mapper currently supports LIMIT orders only")
    if validity not in {"DAY", "IOC"}:
        raise ValueError("Order validity must be DAY or IOC")
    if not algo_id:
        raise ValueError("algo_id is required")

    return INDMoneyOrderRequest(
        txn_type=intent.action.value,
        exchange=exchange,
        segment=segment,
        product=product,
        order_type=order_type,
        validity=validity,
        security_id=str(int(instrument.security_id)),
        qty=int(intent.quantity),
        algo_id=algo_id,
        limit_price=float(intent.limit_price),
        is_amo=bool(is_amo),
        remarks=str(intent.client_order_id),
    )
