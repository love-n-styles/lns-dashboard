import streamlit as st
#import streamlit.components.v1 as components
import configparser as cp
import mysql.connector as db
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def show():
    st.title('Performance - Current Year')

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
        port=config["DB"]["port"],
        password=config["DB"]["pass"],
        database=config["DB"]["schema"]
    )

    cell_a1, cell_a2, cell_a3 = st.columns(3)
    with cell_a1:
        st.text("YTD Revenue")

    with cell_a2:
        st.text("YTD Booking Taken")

    with cell_a3:
        st.text("YTD COGS")

    cell_b1, cell_b2 = st.columns(2)
    with cell_b1:
        st.text("Monthly Income vs Cost Trend")
        cursor = cn.cursor()
        query = config["SQL"]["income-cy"]
        current_year = 2020
        cursor.execute(query, (current_year,))
        df = pd.DataFrame(cursor.fetchall())
        df.rename(columns={0: 'Month', 1: 'Amount'}, inplace=True)
        fig = px.line(df, x="Month", y="Amount", hover_data=[
                      "Amount"], labels={"Amount": "Amount (PHP)"})
        st.plotly_chart(fig)

    with cell_b2:
        st.text("Monthly Revenue by Location")
