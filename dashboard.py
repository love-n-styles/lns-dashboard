import streamlit as st
import mysql.connector as db

# import dashboard pages
from pages import perf_cy
from pages import perf_py
from pages import cost_mgt
from pages import perf_loc
from pages import event_calendar
from pages import metadata

if __name__ == "__main__":
    st.set_page_config(
        # Can be "centered" or "wide". In the future also "dashboard", etc.
        layout="wide",
        initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
        # String or None. Strings get appended with "• Streamlit".
        page_title="Dashboard",
        page_icon=None,  # String, anything supported by st.image, or None.
    )

    cn = db.connect(
        host=st.secrets.db.db_host,
        port=st.secrets.db.db_port,
        user=st.secrets.db.db_user,
        password=st.secrets.db.db_password,
        database=st.secrets.db.db_database,
    )

    PAGES = {
        "Performance - Current Year": perf_cy,
        "Performance - All Years": perf_py,
        "Costs - All Years": cost_mgt,
        "Performance by Location": perf_loc,
        "Event Calendar": event_calendar,
        "Data Readiness": metadata
    }

    st.sidebar.title('Navigation')
    #page1 = st.sidebar.selectbox("Go to page:", list(PAGES.keys()))
    # page1.show()
    page_selection = st.sidebar.radio("Select a page:", list(PAGES.keys()))
    page = PAGES[page_selection]
    page.show(cn)
