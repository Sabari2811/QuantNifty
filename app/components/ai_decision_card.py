import streamlit as st

from decision.constants import Signal


_REASON_LABELS = {
    "Dealers Long Gamma": "Long Gamma",
    "Dealers Short Gamma": "Short Gamma",
    "Positive Delta": "Positive Delta",
    "Negative Delta": "Negative Delta",
    "Positive Vanna": "Positive Vanna",
    "Negative Vanna": "Negative Vanna",
    "Above Support": "Above Support",
    "Below Resistance": "Below Resistance",
    "Institutional Absorption": "Institutional Absorption",
    "Gamma Flip": "Gamma Flip",
    "Positive GEX": "Positive GEX",
    "Negative GEX": "Negative GEX",
    "Inside Expected Move": "Inside Expected Move",
    "Low Expected Volatility": "Low Volatility",
    "High Expected Volatility": "High Volatility",
    "Range Market": "Range Market",
}


def _compact_reasons(reasons, limit=3):
    """Return a short, de-duplicated set of readable decision factors."""
    compact = []
    seen = set()

    for reason in reasons or []:
        label = _REASON_LABELS.get(reason, reason)
        if label in seen:
            continue
        seen.add(label)
        compact.append(label)
        if len(compact) >= limit:
            break

    return compact


def show(ctx):

    decision = ctx.decision

    execution = decision.trade.execution

    st.subheader("🤖 AI Decision")

    with st.container(border=True):

        # --------------------------------------------------
        # Signal
        # --------------------------------------------------

        if decision.signal.name == Signal.BUY_CALL.value:

            st.success("🟢 BUY CALL")

        elif decision.signal.name == Signal.BUY_PUT.value:

            st.error("🔴 BUY PUT")

        else:

            st.warning("🟡 WAIT")

        # --------------------------------------------------
        # Confidence
        # --------------------------------------------------

        confidence = decision.signal.confidence

        st.write(f"Confidence : {confidence}%")

        st.progress(confidence / 100)

        st.divider()

        # --------------------------------------------------
        # Trade Quality
        # --------------------------------------------------

        if decision.signal.name == Signal.WAIT.value:

            st.metric(
                "Trade Quality",
                "--"
            )

        else:

            st.metric(
                "Trade Quality",
                execution.trade_quality
            )

        # --------------------------------------------------
        # Key factors — compact, de-duplicated summary
        # --------------------------------------------------

        factors = _compact_reasons(decision.reasons)

        if factors:
            st.caption("Why: " + " • ".join(factors))
