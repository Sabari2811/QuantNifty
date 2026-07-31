import streamlit as st


def render(df):

    st.subheader("📑 Live Option Chain")

    if df is None or df.empty:
        st.warning("No Option Chain Available")
        return

    table = df.copy()

    # ---------------------------------------
    # Highest OI
    # ---------------------------------------

    max_ce_oi = table["CE_OI"].max()
    max_pe_oi = table["PE_OI"].max()

    max_ce_vol = table["CE_VOLUME"].max()
    max_pe_vol = table["PE_VOLUME"].max()

    # ---------------------------------------
    # Style
    # ---------------------------------------

    def highlight(row):

        style = [""] * len(row)

        columns = list(table.columns)

        if row["CE_OI"] == max_ce_oi:
            style[columns.index("CE_OI")] = \
                "background-color:#006400;color:white;font-weight:bold"

        if row["PE_OI"] == max_pe_oi:
            style[columns.index("PE_OI")] = \
                "background-color:#8B0000;color:white;font-weight:bold"

        if row["CE_VOLUME"] == max_ce_vol:
            style[columns.index("CE_VOLUME")] = \
                "background-color:#1E90FF;color:white"

        if row["PE_VOLUME"] == max_pe_vol:
            style[columns.index("PE_VOLUME")] = \
                "background-color:#1E90FF;color:white"

        return style

    styled = table.style.apply(
        highlight,
        axis=1
    )

    st.dataframe(
        styled,
        use_container_width=True,
        height=420
    )