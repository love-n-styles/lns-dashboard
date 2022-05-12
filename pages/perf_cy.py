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
        st.markdown("## YTD Revenue")
        number1 = 111
        kpi = "{:,}".format(number1)
        st.markdown(
            f"""
            <div style="border-radius: 25px; border: 2px solid #696969; padding: 20px;
                width: 200px; height: 150px;">
            <h1 style='text-align: center; color: #00b300;'>{kpi}</h1>
            </div>
            """, unsafe_allow_html=True)

    with cell_a2:
        st.markdown("## YTD Booking Taken")
        number1 = 98888
        kpi = "{:,}".format(number1)
        st.markdown(
            f"""
            <div style="border-radius: 25px; border: 2px solid #696969; padding: 20px;
                width: 200px; height: 150px;">
            <h1 style='text-align: center; color: #00b300;'>{kpi}</h1>
            </div>
            """, unsafe_allow_html=True)

    with cell_a3:
        st.markdown("## YTD COGS")
        number1 = 12345
        st.markdown(
            f"""
            <div style="border-radius: 25px; border: 2px solid #696969; padding: 20px;
                width: 200px; height: 150px;">
            <h1 style='text-align: center; color: #00b300;'>{number1}</h1>
            </div>
            """, unsafe_allow_html=True)

    cell_b1, cell_b2 = st.columns(2)
    with cell_b1:
        st.markdown("## Monthly Income vs Cost Trend")
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
        st.markdown("## Monthly Revenue by Location")
