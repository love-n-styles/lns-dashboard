import streamlit as st
import configparser as cp
import mysql.connector as db
import pandas as pd
from datetime import datetime
from config import Config

query_year = datetime.now().year
query_month = datetime.now().month
months_in_year = ['Jan', 'Feb', 'Mar', 'Apr', 'May',
                  'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

config = cp.ConfigParser()
config.read("sql.ini")


def show(cn: db.connection):
    st.markdown("# Event Calendar")

    cursor = cn.cursor()
    query = config["sql"]["event-list"]

    with st.container():
        showPrevNextButton("1")

        cursor.execute(query, (query_year, query_month))
        rows = cursor.fetchall()
        if cursor.rowcount > 0:
            df = pd.DataFrame(rows)
            cursor.close()
            df.rename(columns={0: "Day", 1: "Location", 2: "Staff",
                      3: "Receipt#", 4: "Coordinator", 5: "Clients"}, inplace=True)
            #df.style.format({"Date": lambda t: t.strftime("%d %b")})
            st.table(df)

            showPrevNextButton("2")
        else:
            Config.show_no_record_found()


def gotoPrevMonth():
    global query_month
    global query_year
    query_month = query_month - 1
    if query_month < 1:
        query_month = 12
        query_year = query_year - 1


def gotoNextMonth():
    global query_month
    global query_year
    query_month = query_month + 1
    if query_month > 12:
        query_month = 1
        query_year = query_year + 1


def showPrevNextButton(id: str):
    key1 = "prev_month" + id
    key2 = "Next_month" + id

    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("<< Previous Month", key=key1,
                  on_click=gotoPrevMonth)
    with col2:
        st.markdown(
            f"<span align=center><strong>{months_in_year[query_month-1]}-{query_year}</strong></span>", unsafe_allow_html=True)

    with col3:
        st.button("Next Month >>", key=key2,
                  on_click=gotoNextMonth)
