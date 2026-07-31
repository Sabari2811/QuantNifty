import streamlit as st


def show(
    title,
    value,
    icon="",
    subtitle="",
    color="#FFFFFF"
):

    html = f"""
<div style="
background:#1A1F2B;
border:1px solid #2A3242;
border-radius:16px;
padding:18px;
height:140px;
display:flex;
flex-direction:column;
justify-content:space-between;
">

<div style="
color:#9CA3AF;
font-size:14px;
font-weight:600;
">

{icon} {title}

</div>

<div style="
font-size:34px;
font-weight:bold;
color:{color};
">

{value}

</div>

<div style="
font-size:13px;
color:#9CA3AF;
">

{subtitle}

</div>

</div>
"""

    st.markdown(
        html,
        unsafe_allow_html=True
    )