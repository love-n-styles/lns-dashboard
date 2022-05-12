# import dependencies
from datetime import datetime
import streamlit as st
import configparser as cp
import mysql.connector as db
#import pandas as pd
#import numpy as np
#import plotly.express as px
#from plotly.subplots import make_subplots
#import plotly.graph_objects as go
# import matplotlib.pyplot as plt

# import pages
from pages import perf_cy
from pages import perf_py
from pages import cost_mgt

st.set_page_config(
    # Can be "centered" or "wide". In the future also "dashboard", etc.
    layout="wide",
    initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
    # String or None. Strings get appended with "• Streamlit".
    page_title="Dashboard",
    page_icon=None,  # String, anything supported by st.image, or None.
)

config = cp.ConfigParser()
config.read("config.ini")

cn = db.connect(
    host=config["DB"]["host"],
    user=config["DB"]["user"],
    port=config["DB"]["port"],
    password=config["DB"]["pass"],
    database=config["DB"]["schema"]
)

CURRENT_YEAR = datetime.now().year
PREVIOUS_YEAR = CURRENT_YEAR - 1

YEARS = {
    str(CURRENT_YEAR): CURRENT_YEAR,
    str(PREVIOUS_YEAR): PREVIOUS_YEAR,
    "2020": 2020,
    "2019": 2019
}

PAGES = {
    "Performance - Current Year": perf_cy,
    "Performance - Previous Years": perf_py,
    "Costs - Previous Years": cost_mgt,
    "Performance by Location": perf_py
}

st.sidebar.title('Current Year')
year_scope = st.sidebar.selectbox("Select year:", list(YEARS.keys()))

st.sidebar.title('Navigation')
#page1 = st.sidebar.selectbox("Go to page:", list(PAGES.keys()))
# page1.show()
selection = st.sidebar.radio("Select a page:", list(PAGES.keys()))
page = PAGES[selection]
page.show(cn, int(year_scope))
