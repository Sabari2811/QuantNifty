from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any

import streamlit as st


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (tuple, list, set)):
        return [_jsonable(v) for v in value]
    if hasattr(value, "to_dict"):
        try:
            return _jsonable(value.to_dict(orient="records"))
        except TypeError:
            try:
                return _jsonable(value.to_dict())
            except Exception:
                pass
        except Exception:
            pass
    return str(value)


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
