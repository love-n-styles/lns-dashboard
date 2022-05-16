import streamlit as st
import configparser as cp
import mysql.connector as db
import pandas as pd
#import plotly.express as px
#import plotly.graph_objects as go
from config import Config
from pages import event_calendar

config = cp.ConfigParser()
config.read("sql.ini")


def show(cn: db.connection):
    st.markdown("# Data Readiness")
    cursor = cn.cursor()
    query = config["sql"]["metadata"]
    cursor.execute(query)

    rows = cursor.fetchall()
    if cursor.rowcount > 0:
        df = pd.DataFrame(rows)
        cursor.close()
        df.rename(columns={0: "Type", 1: "Last Date"}, inplace=True)
        st.table(df)
    else:
        Config.show_no_record_found()
