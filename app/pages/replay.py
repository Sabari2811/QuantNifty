import streamlit as st

from app.services.replay_service import ReplayService
from app.services.replay_facade import ReplayFacade

from app.components.replay.context_tab import show as context_tab
from app.components.replay.analytics_tab import show as analytics_tab
from app.components.replay.decision_tab import show as decision_tab

from app.components.replay_browser import show as replay_browser


def show():

    st.title("🎬 Replay")

    st.caption(
        "Replay historical QuantNifty sessions."
    )

    st.divider()

    # ==========================================================
    # Services
    # ==========================================================

    replay_service = ReplayService()

    recordings = replay_service.get_recordings()

    selected = replay_browser(recordings)

    # ==========================================================
    # Session State
    # ==========================================================

    if "replay_facade" not in st.session_state:

        st.session_state.replay_facade = ReplayFacade()

        st.session_state.selected_recording = None

    replay = st.session_state.replay_facade

    # ==========================================================
    # Load Recording
    # ==========================================================

    if (
        selected is not None
        and
        st.session_state.selected_recording != selected.folder
    ):

        replay.load(selected)

        st.session_state.selected_recording = selected.folder

    # ==========================================================
    # Session
    # ==========================================================

    st.subheader("Replay Session")

    if not replay.loaded:

        st.info("No replay loaded.")

        return

    controller = replay.controller

    session = controller._session

    c1, c2, c3 = st.columns(3)

    c1.metric(

        "Snapshots",

        session.total

    )

    c2.metric(

        "Current",

        session.index + 1

    )

    c3.metric(

        "Progress",

        f"{session.progress:.0f}%"

    )

    st.divider()

    # ==========================================================
    # Playback
    # ==========================================================

    st.subheader("Playback")

    c1, c2, c3, c4, c5 = st.columns(5)

    previous = c1.button(

        "⏮ Previous",

        width="stretch"

    )

    play = c2.button(

        "▶ Play",

        disabled=True,

        width="stretch"

    )

    pause = c3.button(

        "⏸ Pause",

        disabled=True,

        width="stretch"

    )

    stop = c4.button(

        "⏹ Stop",

        disabled=True,

        width="stretch"

    )

    next_btn = c5.button(

        "⏭ Next",

        width="stretch"

    )

    # ==========================================================
    # Navigation
    # ==========================================================

    if previous:

        replay.previous()

        st.rerun()

    if next_btn:

        replay.next()

        st.rerun()

    # ==========================================================
    # Progress
    # ==========================================================

    st.divider()

    st.subheader("Replay Progress")

    snapshot = session.current()

    st.progress(

        session.progress / 100

    )

    a, b, c = st.columns(3)

    a.metric(

        "Cycle",

        f"{session.index + 1}/{session.total}"

    )

    b.metric(

        "Progress",

        f"{session.progress:.0f}%"

    )

    c.metric(

        "Timestamp",

        snapshot.runtime.get(

            "timestamp",

            "--"

        )

    )

    
    # ==========================================================
    # Replay Inspector
    # ==========================================================

    st.divider()

    st.subheader("Replay Inspector")

    ctx = replay.context()

    if ctx is None:

        st.info("Replay not executed yet.")

    else:

        tabs = st.tabs(
            [
                "Context",
                "Analytics",
                "Decision",
                "Explanation",
                "Greeks",
                "Option Chain",
                "Runtime"
            ]
        )

        #
        # Context
        #
        with tabs[0]:

            context_tab(
                ctx,
                session
            )

        #
        # Analytics
        #
        with tabs[1]:

            analytics_tab(
                ctx
            )

        #
        # Decision
        #
        with tabs[2]:

            decision_tab(ctx)

        #
        # Explanation
        #
        with tabs[3]:

            st.info(
                "Coming Soon"
            )

        #
        # Greeks
        #
        with tabs[4]:

            st.info(
                "Coming Soon"
            )

        #
        # Option Chain
        #
        with tabs[5]:

            st.info(
                "Coming Soon"
            )

        #
        # Runtime
        #
        with tabs[6]:

            st.info(
                "Coming Soon"
            )