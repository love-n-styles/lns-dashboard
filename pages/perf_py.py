import streamlit as st
import configparser as cp
import mysql.connector as db
import pandas as pd
import plotly.express as px
from config import Config

config = cp.ConfigParser()
config.read("sql.ini")

# Layout


def show(cn: db.connection):
    st.markdown("# Performance - All Years")

    cell_a1, cell_a2 = st.columns(2)
    with cell_a1:
        revenue_vs_cost(cn)

    with cell_a2:
        annual_revenue_by_loc(cn)

    cell_b1, cell_b2 = st.columns(2)
    with cell_b1:
        Config.placeholder()

    with cell_b2:
        Config.placeholder()

# Building blocks


def revenue_vs_cost(cn: db.connection):
    st.markdown("### Revenue vs Expenses")
    query = config["sql"]["revenue-vs-expense"]
    cursor = cn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    if cursor.rowcount > 0:
        df = pd.DataFrame(rows)
        cursor.close()
        df.rename(columns={0: "Year", 1: "Type", 2: "Amount"}, inplace=True)
        fig = px.line(df, x="Year", y="Amount", color="Type", hover_data=[
            "Amount"], labels={"Amount": "Amount (PHP)"}, markers=True)
        fig = Config.set_chart_config(fig)

        st.plotly_chart(fig, use_container_width=True)
    else:
        Config.show_no_record_found()


def annual_revenue_by_loc(cn: db.connection):
    st.markdown("### Revenue by Location")
    query = config["sql"]["annual-revenue-loc"]
    cursor = cn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    if cursor.rowcount > 0:
        df = pd.DataFrame(rows)
        cursor.close()
        df.rename(columns={0: "Year", 1: "Location",
                  2: "Amount"}, inplace=True)
        fig = px.line(df, x="Year", y="Amount", color="Location", hover_data=[
            "Amount"], labels={"Amount": "Amount (PHP)"}, markers=True)
        fig = Config.set_chart_config(fig)
        st.plotly_chart(fig, use_container_width=True)
    else:
        Config.show_no_record_found()
