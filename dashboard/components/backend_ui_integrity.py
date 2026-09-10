from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any

import streamlit as st


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(v) for v in value]
    if hasattr(value, "to_dict"):
        try:
            return _jsonable(value.to_dict())
        except Exception:
            pass
    return value


def render(report: dict[str, Any]) -> None:
    """Display the canonical backend -> UI mapping/integrity result."""
    status = report.get("status", "FAIL")
    errors = report.get("errors", ())

    st.subheader("🔗 Backend ↔ UI Integrity")
    if status == "PASS":
        st.success("PASS — UI values are mapped from the canonical backend cycle without competing calculations.")
    else:
        st.error("FAIL — backend/UI mapping divergence detected.")
        for error in errors:
            st.write(f"• {error}")

    contract = report.get("contract", {})
    with st.expander("View canonical UI data contract", expanded=False):
        st.json(_jsonable(contract))
