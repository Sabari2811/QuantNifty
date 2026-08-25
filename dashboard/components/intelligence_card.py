from __future__ import annotations

import streamlit as st


def _value(data, key, default="-"):
    value = data.get(key, default) if isinstance(data, dict) else default
    return default if value is None else value


def _compact_provenance_reasons(reasons):
    """Turn canonical provenance reasons into short, human-readable details."""
    labels = {
        "provider_quote_timestamp_unavailable": "Quote timestamp unavailable",
        "provider_candle_timestamp": "Provider candle timestamp available",
        "freshness_unverified:INDMoney index quote": "Index quote freshness unverified",
        "freshness_unverified:INDMoney option quotes": "Option quote freshness unverified",
        "integrity_suspect:INDMoney option quotes": "Option quote integrity suspect",
        "ce_ltp_below_intrinsic": "CE LTP below intrinsic value",
    }

    compact = []
    seen = set()
    for reason in reasons or ():
        text = labels.get(str(reason), str(reason))
        if text not in seen:
            compact.append(text)
            seen.add(text)
    return compact


def render(intelligence):
    """Render canonical IntelligenceResult data without recomputation."""

    st.subheader("🧠 Intelligence")

    if not intelligence:
        st.info("Intelligence unavailable for this runtime cycle.")
        return

    quality = _value(intelligence, "data_quality", {})
    regime = _value(intelligence, "regime", {})

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Direction", _value(intelligence, "direction"))
    c2.metric("Conviction", f"{float(_value(intelligence, 'conviction', 0.0)):.1f}%")
    c3.metric("Opportunity", f"{float(_value(intelligence, 'opportunity_quality', 0.0)):.1f}%")
    c4.metric("Recommendation", _value(intelligence, "recommendation"))

    st.divider()

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Regime", _value(regime, "regime"))
    c6.metric("Regime Confidence", f"{float(_value(regime, 'confidence', 0.0)):.1f}%")
    c7.metric("Data Coverage", f"{float(_value(quality, 'coverage_score', _value(quality, 'score', 0.0))):.1f}/100")
    c8.metric("Integrity", _value(quality, "integrity_status", _value(quality, "status")))

    freshness = _value(quality, "freshness_status")
    integrity = _value(quality, "integrity_status", _value(quality, "status"))
    reasons = _value(quality, "reasons", ())

    if freshness == "VERIFIED":
        st.success("Freshness: VERIFIED")
    else:
        st.warning("Freshness: UNVERIFIED — provider quote timestamp is unavailable.")

    if integrity == "SUSPECT":
        st.warning("Data integrity: SUSPECT — option quote validation flagged an issue.")
    elif integrity == "UNVERIFIED":
        st.info("Data integrity: UNVERIFIED — no integrity failure was detected.")

    if reasons:
        with st.expander("View data-quality details", expanded=False):
            for reason in _compact_provenance_reasons(reasons):
                st.write(f"• {reason}")

    primary = _value(intelligence, "primary_scenario")
    alternative = _value(intelligence, "alternative_scenario")

    if primary or alternative:
        st.divider()
        c9, c10 = st.columns(2)

        with c9:
            st.markdown("**Primary scenario**")
            if primary:
                st.write(
                    f"{_value(primary, 'name')} — "
                    f"{_value(primary, 'direction')} "
                    f"({_value(primary, 'probability', 0.0):.1f}%)"
                )
                if _value(primary, "trigger", ""):
                    st.caption(f"Trigger: {_value(primary, 'trigger')}")
                if _value(primary, "invalidation", ""):
                    st.caption(
                        f"Invalidation: {_value(primary, 'invalidation')}"
                    )
            else:
                st.caption("Not available")

        with c10:
            st.markdown("**Alternative scenario**")
            if alternative:
                st.write(
                    f"{_value(alternative, 'name')} — "
                    f"{_value(alternative, 'direction')} "
                    f"({_value(alternative, 'probability', 0.0):.1f}%)"
                )
                if _value(alternative, "trigger", ""):
                    st.caption(f"Trigger: {_value(alternative, 'trigger')}")
            else:
                st.caption("Not available")

    explanation = _value(intelligence, "explanation", "")
    if explanation:
        st.caption(explanation)
