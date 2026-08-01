import streamlit as st

from recording.replay_recording import ReplayRecording


def show(recordings: list[ReplayRecording]):

    st.subheader("📂 Replay Browser")

    if not recordings:

        st.info("No recordings found.")

        return None

    labels = []

    for recording in recordings:

        icon = "🟢" if recording.complete else "🟡"

        labels.append(
            f"{icon} {recording.display_name}"
        )

    index = st.selectbox(

        "Available Sessions",

        range(len(labels)),

        format_func=lambda i: labels[i]

    )

    recording = recordings[index]

    st.divider()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Date",
        recording.date
    )

    c2.metric(
        "Cycle",
        recording.cycle
    )

    c3.metric(
        "Status",
        "Complete"
        if recording.complete
        else "Legacy"
    )

    st.divider()

    st.subheader("Files")

    files = {

        "Runtime": recording.runtime,

        "Analytics": recording.analytics,

        "Decision": recording.decision,

        "Explanation": recording.explanation,

        "Greeks": recording.greeks,

        "Option Chain": recording.option_chain,

        "Manifest": recording.manifest

    }

    for name, present in files.items():

        icon = "✅" if present else "❌"

        st.write(
            f"{icon} {name}"
        )

    return recording