import streamlit as st
import configparser as cp
import mysql.connector as db
import pandas as pd
import plotly.express as px

config = cp.ConfigParser()
config.read("config.ini")

# Layout


def show(cn: db.connection, year_scope: int):
    st.markdown(f"# Performance - {year_scope}")

    cell_a1, cell_a2, cell_a3 = st.columns(3)
    with cell_a1:
        kpi_ytd_revenue(cn, year_scope)

    with cell_a2:
        kpi_ytd_bookings(cn, year_scope)

    with cell_a3:
        kpi_ytd_cogs(cn, year_scope)

    cell_b1, cell_b2 = st.columns(2)
    with cell_b1:
        chart_monthly_revenue_vs_cost(cn, year_scope)

    with cell_b2:
        chart_monthly_revenue_by_loc(cn, year_scope)

# Building blocks


def kpi_ytd_revenue(cn: db.connection, year_scope: int):
    st.markdown("## YTD Revenue")
    query = config["SQL"]["ytd-revenue-cy"]
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
        <h1 style='text-align: center; color: #00b300;'>{kpi}</h1>
        </div>
        """, unsafe_allow_html=True)


def kpi_ytd_bookings(cn: db.connection, year_scope: int):
    st.markdown("## YTD Booking Taken")
    retval = 98888
    kpi = "{:,}".format(retval)
    st.markdown(
        f"""
        <div style="border-radius: 25px; border: 2px solid #696969; padding: 20px;
            width: 100%;">
        <h1 style='text-align: center; color: #00b300;'>{kpi}</h1>
        </div>
        """, unsafe_allow_html=True)


def kpi_ytd_cogs(cn: db.connection, year_scope: int):
    st.markdown("## YTD COGS")
    query = config["SQL"]["ytd-cogs-cy"]
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
        <h1 style='text-align: center; color: #00b300;'>{kpi}</h1>
        </div>
        """, unsafe_allow_html=True)


def chart_monthly_revenue_vs_cost(cn: db.connection, year_scope: int):
    st.markdown("## Monthly Income vs Cost Trend")
    query = config["SQL"]["ytd-revenue-vs-expense-cy"]
    cursor = cn.cursor()
    cursor.execute(query, (year_scope,))
    rows = cursor.fetchall()
    if cursor.rowcount > 0:
        df = pd.DataFrame(rows)
        cursor.close()
        df.rename(columns={0: "Month", 1: "Type",
                           2: "Amount"}, inplace=True)
        fig = px.line(df, x="Month", y="Amount", color="Type", hover_data=[
            "Amount"], labels={"Amount": "Amount (PHP)"})
        # fig.update_layout(showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    st.write(cursor.rowcount, " rows returned")


def chart_monthly_revenue_by_loc(cn: db.connection, year_scope: int):
    st.markdown("## Monthly Revenue by Location")
    query = config["SQL"]["ytd-revenue-loc-cy"]
    cursor = cn.cursor()
    cursor.execute(query, (year_scope,))
    rows = cursor.fetchall()
    if cursor.rowcount > 0:
        df = pd.DataFrame(rows)
        cursor.close()
        df.rename(columns={0: "Month", 1: "Location",
                           2: "Amount"}, inplace=True)
        fig = px.line(df, x="Month", y="Amount", color="Location", hover_data=[
            "Amount"], labels={"Amount": "Amount (PHP)"})
        # fig.update_layout(showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    st.write(cursor.rowcount, " rows returned")


def placeholder(cn: db.connection, year_scope: int):
    st.markdown("### Placeholder")
