import streamlit as st

from app.pages import (
    dashboard,
    portfolio,
    performance,
    journal,
)


PAGES = {
    "🏠 Dashboard": dashboard.show,
    "💼 Portfolio": portfolio.show,
    "📈 Performance": performance.show,
    "📒 Journal": journal.show,
}


def main():
    st.set_page_config(
        page_title="QuantNifty",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.sidebar.title("QuantNifty")

    page = st.sidebar.radio(
        "Navigation",
        list(PAGES.keys()),
    )

    PAGES[page]()


if __name__ == "__main__":
    main()