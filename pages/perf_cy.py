import streamlit as st
import configparser as cp
import mysql.connector as db
import pandas as pd
import plotly.express as px
from config import Config
from datetime import datetime


CURRENT_YEAR = datetime.now().year
PREVIOUS_YEAR = CURRENT_YEAR - 1

YEARS = {
    str(CURRENT_YEAR): CURRENT_YEAR,
    str(PREVIOUS_YEAR): PREVIOUS_YEAR,
    "2020": 2020,
    "2019": 2019
}
year_scope = CURRENT_YEAR

config = cp.ConfigParser()
config.read("sql.ini")

# Layout


def show(cn: db.connection):
    global year_scope
    st.sidebar.title('Current Year')
    year_scope = st.sidebar.selectbox("Select year:", list(YEARS.keys()))

    st.markdown(f"# Performance - {year_scope}")

    cell_a1, cell_a2, cell_a3, cell_a4 = st.columns(4)
    with cell_a1:
        kpi_ytd_revenue(cn, year_scope)

    with cell_a2:
        kpi_ytd_bookings(cn, year_scope)

    with cell_a3:
        kpi_ytd_cogs(cn, year_scope)

    with cell_a4:
        Config.placeholder("Upcoming Revenue")

    cell_b1, cell_b2 = st.columns(2)
    with cell_b1:
        chart_monthly_revenue_vs_expenses(cn, year_scope)

    with cell_b2:
        chart_monthly_revenue_by_loc(cn, year_scope)

    cell_c1, cell_c2 = st.columns(2)
    with cell_c1:
        st.markdown("## Booking Taken by Location")
        Config.placeholder()

    with cell_c2:
        st.markdown("## Upcoming Revenue")
        Config.placeholder()

# Building blocks


def kpi_ytd_revenue(cn: db.connection, year_scope: int):
    st.markdown("## Revenue")
    query = config["sql"]["ytd-revenue-cy"]
    cursor = cn.cursor()
    cursor.execute(query, (year_scope,))
    row = cursor.fetchone()
    retval = row[0]
    if retval is None:
        retval = 0
    kpi = "{:,}".format(retval)
    st.markdown(
        f"""
        <div style="border-radius: 25px; border: 2px solid #696969; padding: 20px;
            width: 100%;">
        <h2 style='text-align: center; color: #00b300;'>{kpi}</h2>
        </div>
        """, unsafe_allow_html=True)


def kpi_ytd_bookings(cn: db.connection, year_scope: int):
    st.markdown("## Booking Taken")
    retval = 98888
    kpi = "{:,}".format(retval)
    st.markdown(
        f"""
        <div style="border-radius: 25px; border: 2px solid #696969; padding: 20px;
            width: 100%;">
        <h2 style='text-align: center; color: #00b300;'>{kpi}</h2>
        </div>
        """, unsafe_allow_html=True)


def kpi_ytd_cogs(cn: db.connection, year_scope: int):
    st.markdown("## COGS")
    query = config["sql"]["ytd-cogs-cy"]
    cursor = cn.cursor()
    cursor.execute(query, (year_scope,))
    row = cursor.fetchone()
    retval = row[0]
    if retval is None:
        retval = 0
    kpi = "{:,}".format(retval)
    st.markdown(
        f"""
        <div style="border-radius: 25px; border: 2px solid #696969; padding: 20px;
            width: 100%;">
        <h2 style='text-align: center; color: #00b300;'>{kpi}</h2>
        </div>
        """, unsafe_allow_html=True)


def chart_monthly_revenue_vs_expenses(cn: db.connection, year_scope: int):
    st.markdown("## Revenue vs Expenses")
    query = config["sql"]["ytd-revenue-vs-expense-cy"]
    cursor = cn.cursor()
    cursor.execute(query, (year_scope,))
    rows = cursor.fetchall()
    if cursor.rowcount > 0:
        df = pd.DataFrame(rows)
        cursor.close()
        df.rename(columns={0: "Month", 1: "Type",
                           2: "Amount"}, inplace=True)
        fig = px.line(df, x="Month", y="Amount", color="Type", hover_data=[
            "Amount"], labels={"Amount": "Amount (PHP)"}, markers=True)
        fig = Config.set_chart_config(fig)

        st.plotly_chart(fig, use_container_width=True)
    else:
        Config.show_no_record_found()


def chart_monthly_revenue_by_loc(cn: db.connection, year_scope: int):
    st.markdown("## Revenue by Location")
    query = config["sql"]["ytd-revenue-loc-cy"]
    cursor = cn.cursor()
    cursor.execute(query, (year_scope,))
    rows = cursor.fetchall()
    if cursor.rowcount > 0:
        df = pd.DataFrame(rows)
        cursor.close()
        df.rename(columns={0: "Month", 1: "Location",
                           2: "Amount"}, inplace=True)
        fig = px.line(df, x="Month", y="Amount", color="Location", hover_data=[
            "Amount"], labels={"Amount": "Amount (PHP)"}, markers=True)
        fig = Config.set_chart_config(fig)

        st.plotly_chart(fig, use_container_width=True)
    else:
        Config.show_no_record_found()
