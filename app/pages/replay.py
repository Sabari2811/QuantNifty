import streamlit as st

from app.services.replay_service import ReplayService
from app.components.replay_browser import show as replay_browser


def show():

    service = ReplayService()

    recordings = service.get_recordings()

    selected = replay_browser(recordings)

    st.title("🎬 Replay")

    st.caption(
        "Replay historical market sessions using the LiveEngine."
    )

    st.divider()

    # ==========================================================
    # Session
    # ==========================================================

    st.subheader("Replay Session")

    st.info(
        "No replay session loaded."
    )

    st.divider()

    # ==========================================================
    # Playback Controls
    # ==========================================================

    st.subheader("Playback")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.button(
            "⏮ Previous",
            disabled=True,
            use_container_width=True,
        )

    with c2:
        st.button(
            "▶ Play",
            disabled=True,
            use_container_width=True,
        )

    with c3:
        st.button(
            "⏸ Pause",
            disabled=True,
            use_container_width=True,
        )

    with c4:
        st.button(
            "⏹ Stop",
            disabled=True,
            use_container_width=True,
        )

    with c5:
        st.button(
            "⏭ Next",
            disabled=True,
            use_container_width=True,
        )

    st.divider()

    # ==========================================================
    # Replay Speed
    # ==========================================================

    st.subheader("Replay Speed")

    st.select_slider(
        "",
        options=[1, 2, 5, 10, 25, 50],
        value=1,
        disabled=True,
    )

    st.divider()

    # ==========================================================
    # Replay Progress
    # ==========================================================

    st.subheader("Progress")

    st.progress(0)

    a, b, c = st.columns(3)

    a.metric("Cycle", "0 / 0")

    b.metric("Progress", "0%")

    c.metric("Timestamp", "--")

    st.divider()

    st.success(
        "Replay architecture initialized. "
        "Playback integration begins in Sprint 2."
    )