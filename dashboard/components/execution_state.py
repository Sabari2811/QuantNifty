from __future__ import annotations

from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any

import streamlit as st


def _plain(value: Any) -> Any:
    if is_dataclass(value):
        return _plain(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    if hasattr(value, "to_dict"):
        try:
            return _plain(value.to_dict())
        except Exception:
            pass
    return value


def render(contract: dict[str, Any]) -> None:
    """Render canonical execution/recovery state passed through DashboardData."""
    execution = contract.get("execution", {})
    runtime = contract.get("runtime", {})
    position = contract.get("position_state", {})

    st.subheader("⚡ Execution & Position State")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Execution Lifecycle", runtime_value(execution.get("lifecycle")))

    result = execution.get("result")
    result_status = getattr(result, "status", None)
    if isinstance(result_status, Enum):
        result_status = result_status.value
    c2.metric("Execution Result", runtime_value(result_status))
    c3.metric("Trade Status", runtime_value(runtime.get("trade_status")))
    c4.metric("Open Position", "YES" if position.get("position") is not None else "NO")

    intent = execution.get("intent")
    if intent is not None:
        with st.expander("Order intent", expanded=False):
            st.json(_plain(intent))
    if result is not None:
        with st.expander("Execution result", expanded=False):
            st.json(_plain(result))

    recovery = position.get("recovery")
    reconciliation = position.get("reconciliation")
    if recovery is not None or reconciliation is not None:
        with st.expander("Recovery / reconciliation", expanded=False):
            st.json({
                "recovery": _plain(recovery),
                "reconciliation": _plain(reconciliation),
            })


def runtime_value(value: Any) -> str:
    if value is None or value == "":
        return "UNAVAILABLE"
    return str(value)
