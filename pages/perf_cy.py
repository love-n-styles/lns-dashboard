import streamlit as st
import configparser as cp
import mysql.connector as db
import pandas as pd
import plotly.express as px
from datetime import datetime
from config import Config

NUMBER_FORMAT = "{:,.0f}"
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
        kpi_future_revenue(cn, year_scope)

    cell_b1, cell_b2 = st.columns(2)
    with cell_b1:
        chart_monthly_revenue_vs_expenses(cn, year_scope)

    with cell_b2:
        chart_monthly_revenue_by_loc(cn, year_scope)

    cell_c1, cell_c2 = st.columns(2)
    with cell_c1:
        chart_booking_by_loc(cn, year_scope)

    with cell_c2:
        chart_future_revenue(cn, year_scope)
        # Config.placeholder("Test")

# Building blocks


def kpi_ytd_revenue(cn: db.connection, year_scope: int):
    st.markdown("### Revenue")
    query = config["sql"]["ytd-revenue-cy"]
    cursor = cn.cursor()
    cursor.execute(query, (year_scope,))
    row = cursor.fetchone()
    retval = row[0]
    if retval is None:
        retval = 0
    kpi = NUMBER_FORMAT.format(retval)
    st.markdown(
        f"""
        <div style="border-radius: 25px; border: 2px solid #696969; padding: 20px;
            width: 100%;">
        <h2 style='text-align: center; color: #00b300;'>{kpi}</h2>
        </div>
        """, unsafe_allow_html=True)


def kpi_ytd_bookings(cn: db.connection, year_scope: int):
    st.markdown("### Booking Taken")
    query = config["sql"]["ytd-booking-taken"]
    cursor = cn.cursor()
    cursor.execute(query, (year_scope,))
    row = cursor.fetchone()
    retval = row[0]
    if retval is None:
        retval = 0
    kpi = NUMBER_FORMAT.format(retval)
    st.markdown(
        f"""
        <div style="border-radius: 25px; border: 2px solid #696969; padding: 20px;
            width: 100%;">
        <h2 style='text-align: center; color: #00b300;'>{kpi}</h2>
        </div>
        """, unsafe_allow_html=True)


def kpi_ytd_cogs(cn: db.connection, year_scope: int):
    st.markdown("### COGS")
    query = config["sql"]["ytd-cogs-cy"]
    cursor = cn.cursor()
    cursor.execute(query, (year_scope,))
    row = cursor.fetchone()
    retval = row[0]
    if retval is None:
        retval = 0
    kpi = NUMBER_FORMAT.format(retval)
    st.markdown(
        f"""
        <div style="border-radius: 25px; border: 2px solid #696969; padding: 20px;
            width: 100%;">
        <h2 style='text-align: center; color: #00b300;'>{kpi}</h2>
        </div>
        """, unsafe_allow_html=True)


def kpi_future_revenue(cn: db.connection, year_scope: int):
    st.markdown("### Future Revenue")
    query = config["sql"]["future-revenue-total"]
    cursor = cn.cursor()
    cursor.execute(query)
    row = cursor.fetchone()
    retval = row[0]
    if retval is None:
        retval = 0
    kpi = NUMBER_FORMAT.format(retval)
    st.markdown(
        f"""
        <div style="border-radius: 25px; border: 2px solid #696969; padding: 20px;
            width: 100%;">
        <h2 style='text-align: center; color: #00b300;'>{kpi}</h2>
        </div>
        """, unsafe_allow_html=True)


def chart_monthly_revenue_vs_expenses(cn: db.connection, year_scope: int):
    st.markdown("### Revenue vs Expenses")
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
    st.markdown("### Revenue by Location")
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


def chart_booking_by_loc(cn: db.connection, year_scope: int):
    st.markdown("### Booking Taken by Location")
    query = config["sql"]["ytd-booking-taken-loc"]
    cursor = cn.cursor()
    cursor.execute(query, (year_scope,))
    rows = cursor.fetchall()
    if cursor.rowcount > 0:
        df = pd.DataFrame(rows)
        cursor.close()
        df.rename(columns={0: "Month", 1: "Location",
                           2: "Event"}, inplace=True)
        fig = px.line(df, x="Month", y="Event", color="Location", hover_data=[
            "Event"], labels={"Event": "No. of Events"}, markers=True)
        fig = Config.set_chart_config(fig, ytick=1)
        # fig.update_yaxes(dtick=1)
        st.plotly_chart(fig, use_container_width=True)
    else:
        Config.show_no_record_found()


def chart_future_revenue(cn: db.connection, year_scope: int):
    st.markdown("### Upcoming Revenue")
    query = config["sql"]["future-revenue-monthly"]
    cursor = cn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    if cursor.rowcount > 0:
        df = pd.DataFrame(rows)
        cursor.close()
        df.rename(columns={0: "Month", 1: "Amount"}, inplace=True)
        # s = df.style.format({"Month": lambda x: "{%b-%Y}".format(x)})
        # df['Month'] = pd.to_datetime(df["Month"], format="%b-%Y", utc=True)
        #df["Month"] = pd.to_datetime(df["Month"].dt.strftime("%b-%Y"))
        #df.style.format({"Month": lambda t: t.strftime("%m-%Y")})
        fig = px.line(df, x="Month", y="Amount", hover_data=[
                      "Amount"], labels={"Amount": "Amount (PHP)"}, markers=True)
        fig = Config.set_chart_config(fig, xtick=0)
        st.plotly_chart(fig, use_container_width=True)
    else:
        Config.show_no_record_found()
