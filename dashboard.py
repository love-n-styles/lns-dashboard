import streamlit as st
import configparser as cp
import mysql.connector as db
import pandas as pd
#import numpy as np
import plotly.express as px
#from plotly.subplots import make_subplots
import plotly.graph_objects as go
# import matplotlib.pyplot as plt

st.set_page_config(
    # Can be "centered" or "wide". In the future also "dashboard", etc.
    layout="wide",
    initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
    # String or None. Strings get appended with "• Streamlit".
    page_title="Dashboard",
    page_icon=None,  # String, anything supported by st.image, or None.
)

st.title('Performance Dashboard')

config = cp.ConfigParser()
config.read("config.ini")
db_host = config["DB"]["host"]
db_port = config["DB"]["port"]
db_schema = config["DB"]["schema"]
db_user = config["DB"]["user"]
db_pass = config["DB"]["pass"]

cn = db.connect(
    host=config["DB"]["host"],
    user=config["DB"]["user"],
    password=config["DB"]["pass"]
)

with cn.cursor() as cur:
    cur.execute(
        "select trans_type, biz_line from lns_finance.journal_view_1 LIMIT 10")
    rows = cur.fetchall()

cell_a1, cell_a2 = st.columns(2)
with cell_a1:
    st.text('Dashboard of Company ABC')
    # Print results.
    for row in rows:
        st.write(f"{row[0]} has a {row[1]}")

with cell_a2:
    st.text("Table")  # time.strftime("%Y-%m-%d %H:%M")

cell_b1, cell_b2 = st.columns(2)
with cell_b1:
    st.text('Dashboard of Company ABC')

with cell_b2:
    st.text("Table")  # time.strftime("%Y-%m-%d %H:%M")
    # Print results.
    for row in rows:
        st.write(f"{row[0]} has a {row[1]}")
