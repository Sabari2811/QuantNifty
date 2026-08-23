from __future__ import annotations

import streamlit as st


def _value(data, key, default="-"):
    value = data.get(key, default) if isinstance(data, dict) else default
    return default if value is None else value


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
    c7.metric("Data Quality", f"{float(_value(quality, 'score', 0.0)):.1f}/100")
    c8.metric("Quality State", _value(quality, "status"))

    freshness = _value(quality, "freshness_status")
    if freshness == "VERIFIED":
        st.success("Freshness: VERIFIED")
    else:
        st.warning(
            "Freshness: UNVERIFIED — this is not the same as stale. "
            "The current provider does not supply a usable quote timestamp."
        )

    reasons = _value(quality, "reasons", ())
    if reasons:
        with st.expander("Data-quality provenance"):
            for reason in reasons:
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
