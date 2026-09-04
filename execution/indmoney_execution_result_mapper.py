from __future__ import annotations

from datetime import datetime

from execution.execution_contract import ExecutionResult, ExecutionStatus, OrderIntent


_TERMINAL_SUCCESS = {"SUCCESS", "EXECUTED", "COMPLETE", "COMPLETED"}
_SUBMITTED = {"QUEUED", "O-PENDING", "PROCESSING", "INITIATED", "PENDING", "MODIFIED"}
_REJECTED = {"ABORTED", "CANCELLED", "EXPIRED", "FAILED", "REJECTED"}
_PARTIAL = {"PARTIALLY FILLED", "PARTIALLY FILLED - CANCELLED", "PARTIALLY FILLED - EXPIRED"}


def _provider_status(payload: dict) -> str:
    data = payload.get("data")
    if not isinstance(data, dict):
        return ""
    return str(data.get("order_status") or data.get("status") or "").strip().upper()


def map_indmoney_execution_result(
    intent: OrderIntent,
    response: dict,
    *,
    timestamp: datetime | None = None,
) -> ExecutionResult:
    """Map one INDMoney order response into the canonical execution contract."""
    if intent is None:
        raise ValueError("Order intent is required")
    if not isinstance(response, dict):
        raise ValueError("INDMoney order response must be a dictionary")

    data = response.get("data")
    if not isinstance(data, dict):
        raise ValueError("INDMoney order response data is missing")

    order_id = str(data.get("order_id") or data.get("id") or "").strip()
    status = _provider_status(response)
    if not order_id:
        return ExecutionResult(
            status=ExecutionStatus.FAILED,
            intent=intent,
            reason="INDMoney order response did not contain broker order ID",
            timestamp=timestamp or datetime.now(),
            raw=response,
        )

    if status in _TERMINAL_SUCCESS:
        canonical = ExecutionStatus.EXECUTED
    elif status in _SUBMITTED or status in _PARTIAL:
        canonical = ExecutionStatus.SUBMITTED
    elif status in _REJECTED:
        canonical = ExecutionStatus.REJECTED
    else:
        canonical = ExecutionStatus.UNKNOWN

    filled_raw = data.get("traded_qty", data.get("filled_quantity", data.get("filled_qty", 0)))
    try:
        filled_quantity = int(filled_raw or 0)
    except (TypeError, ValueError):
        filled_quantity = 0

    average_raw = data.get("average_price", data.get("avg_price", data.get("traded_price")))
    try:
        average_fill_price = float(average_raw) if average_raw is not None else None
    except (TypeError, ValueError):
        average_fill_price = None

    reason = str(data.get("reason") or data.get("message") or status or "").strip()

    return ExecutionResult(
        status=canonical,
        intent=intent,
        broker_order_id=order_id,
        filled_quantity=max(0, filled_quantity),
        average_fill_price=average_fill_price,
        reason=reason,
        timestamp=timestamp or datetime.now(),
        raw=response,
    )
