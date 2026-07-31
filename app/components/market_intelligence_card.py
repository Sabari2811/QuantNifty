import streamlit as st


def _status_color(recommendation: str):

    recommendation = recommendation.upper()

    if recommendation == "BUY CALL":
        return "🟢"

    if recommendation == "BUY PUT":
        return "🔴"

    return "🟡"


def _confidence_label(confidence: int):

    if confidence >= 80:
        return "Very High"

    if confidence >= 60:
        return "High"

    if confidence >= 40:
        return "Moderate"

    if confidence >= 20:
        return "Low"

    return "Very Low"


def show(explanation):

    st.subheader("🧠 Market Intelligence")

    if explanation is None:

        st.info("Market Intelligence not available.")

        return

    # ==========================================================
    # MARKET STATUS
    # ==========================================================

    icon = _status_color(explanation.recommendation)

    confidence_text = _confidence_label(
        explanation.confidence
    )

    st.markdown("## Market Status")

    st.success(
        f"""
{icon} **{explanation.recommendation}**

Confidence : **{explanation.confidence}%**

Conviction : **{confidence_text}**
"""
    )

    st.progress(
        explanation.confidence / 100
    )

    st.divider()

    # ==========================================================
    # MARKET NARRATIVE
    # ==========================================================

    st.markdown("## 📖 Institutional Narrative")

    st.info(
        explanation.narrative
    )

    st.divider()

    # ==========================================================
    # WHY
    # ==========================================================

    st.markdown("## ✅ Why did the engine decide this?")

    if explanation.why:

        for reason in explanation.why:

            if "Weak" in reason or \
               "Low" in reason or \
               "SHORT" in reason or \
               "Negative" in reason:

                st.error(reason)

            else:

                st.success(reason)

    st.divider()

    # ==========================================================
    # WHAT TO WATCH
    # ==========================================================

    st.markdown("## 👀 What should change?")

    if explanation.triggers:

        for trigger in explanation.triggers:

            st.checkbox(
                trigger,
                value=False,
                disabled=True
            )

    else:

        st.info(
            "No future trigger available."
        )