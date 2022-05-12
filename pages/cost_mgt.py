import streamlit as st
import configparser as cp
import mysql.connector as db
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import Config

BIZ_LINES = {
    "*ALL": "*",
    "Bridal": "Bridal",
    "Fashion": "Fashion",
    "Jewellery": "Jewellery",
    "Beauty": "Beauty"
}
biz_line = "*"

config = cp.ConfigParser()
config.read("sql.ini")

# Layout


def show(cn: db.connection):
    global biz_line
    if biz_line == "*":
        st.markdown("# Cost Management")
    else:
        st.markdown(f"# Cost Management for {biz_line}")
    st.sidebar.title('Business Line')
    biz_line_selection = st.sidebar.radio(
        "Selection:", list(BIZ_LINES.keys()))
    biz_line = BIZ_LINES[biz_line_selection]

    cell_a1, cell_a2 = st.columns(2)
    with cell_a1:
        major_cost_by_catg(cn)

    with cell_a2:
        major_non_cogs_by_catg(cn)

    cell_b1, cell_b2 = st.columns(2)
    with cell_b1:
        major_suppliers(cn)

    with cell_b2:
        Config.placeholder()

# Building blocks


def major_cost_by_catg(cn: db.connection):
    st.markdown("## Major Cost Categories")
    cursor = cn.cursor()
    if biz_line == "*":
        query = config["sql"]["major-cost-catg"]
        cursor.execute(query)
    else:
        query = config["sql"]["major-cost-catg-by-line"]
        cursor.execute(query, (biz_line,))

    rows = cursor.fetchall()
    if cursor.rowcount > 0:
        df = pd.DataFrame(rows)
        cursor.close()
        df.rename(columns={0: "Year", 1: "Category",
                  2: "Amount"}, inplace=True)
        fig = px.line(df, x="Year", y="Amount", color="Category", hover_data=[
            "Amount"], labels={"Amount": "Amount (PHP)"})
        fig = Config.set_chart_config(fig)
        st.plotly_chart(fig, use_container_width=True)
    else:
        Config.show_no_record_found()


def major_non_cogs_by_catg(cn: db.connection):
    st.markdown("## Non-COGS Categories")
    cursor = cn.cursor()
    if biz_line == "*":
        query = config["sql"]["major-non-cogs-catg"]
        cursor.execute(query)
    else:
        query = config["sql"]["major-non-cogs-catg-by-line"]
        cursor.execute(query, (biz_line,))

    rows = cursor.fetchall()
    if cursor.rowcount > 0:
        df = pd.DataFrame(rows)
        cursor.close()
        df.rename(columns={0: "Year", 1: "Category",
                  2: "Amount"}, inplace=True)
        fig = px.line(df, x="Year", y="Amount", color="Category", hover_data=[
            "Amount"], labels={"Amount": "Amount (PHP)"})
        fig = Config.set_chart_config(fig)
        st.plotly_chart(fig, use_container_width=True)
    else:
        Config.show_no_record_found()


def major_suppliers(cn: db.connection):
    st.markdown("## Major Suppliers")
    cursor = cn.cursor()
    if biz_line == "*":
        query = config["sql"]["major-suppliers"]
        cursor.execute(query)
    else:
        query = config["sql"]["major-suppliers-by-line"]
        cursor.execute(query, (biz_line,))

    rows = cursor.fetchall()
    if cursor.rowcount > 0:
        df = pd.DataFrame(rows)
        cursor.close()
        df.rename(columns={0: "Supplier", 1: "Amount"}, inplace=True)
        st.table(df)
    else:
        Config.show_no_record_found()
