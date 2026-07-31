import streamlit as st


def render(liquidity):

    st.subheader("🏛 Liquidity")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Support",
        liquidity["support"]
    )

    c2.metric(
        "Resistance",
        liquidity["resistance"]
    )

    c3.metric(
        "Call Wall",
        liquidity["call_wall"]
    )

    c4.metric(
        "Put Wall",
        liquidity["put_wall"]
    )

    st.divider()

    c1, c2 = st.columns(2)

    with c1:

        st.markdown("### 🔴 Top Call Walls")

        for wall in liquidity["top_call_walls"]:

            st.write(
                f"{wall['Strike']}  |  OI : {wall['CE_OI']:,}"
            )

    with c2:

        st.markdown("### 🟢 Top Put Walls")

        for wall in liquidity["top_put_walls"]:

            st.write(
                f"{wall['Strike']}  |  OI : {wall['PE_OI']:,}"
            )

    st.divider()

    imbalance = liquidity["order_imbalance"]

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Pressure",
        imbalance["pressure"]
    )

    c2.metric(
        "OI PCR",
        round(float(imbalance["oi_ratio"]), 2)
    )

    c3.metric(
        "Volume PCR",
        round(float(imbalance["volume_ratio"]), 2)
    )

    st.divider()

    st.markdown("### ⚡ Liquidity Voids")

    st.write(
        f"Void Count : {liquidity['voids']['void_count']}"
    )

    if liquidity["voids"]["void_levels"]:

        st.dataframe(
            liquidity["voids"]["void_levels"],
            use_container_width=True
        )

    st.divider()

    st.markdown("### 🧲 Absorption")

    st.write(
        f"Signals : {liquidity['absorption']['count']}"
    )

    if liquidity["absorption"]["levels"]:

        st.dataframe(
            liquidity["absorption"]["levels"],
            use_container_width=True
        )