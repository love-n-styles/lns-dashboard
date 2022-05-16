from ast import Str
import string
from turtle import onclick
import streamlit as st
import mysql.connector as db
import pandas as pd
from datetime import datetime
from config import Config

query_year = datetime.now().year
query_month = datetime.now().month
# months_in_year = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
months_in_year = ['Jan', 'Feb', 'Mar', 'Apr', 'May',
                  'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def show(cn: db.connection):
    st.markdown("# Event Calendar")

    cursor = cn.cursor()
    query = """select event_date, left(dayname(event_date),3) as event_weekday,
        trans_biz_loc, staff_alias, receipt_number, coordinator_name, client_names
        from client_booking a left join staff b on a.staff_id = b.staff_id
        where is_final = 0 and year(event_date) = %s and month(event_date) = %s
        order by event_date
        """
    with st.container():
        showPrevNextButton("1")

        cursor.execute(query, (query_year, query_month))
        rows = cursor.fetchall()
        if cursor.rowcount > 0:
            df = pd.DataFrame(rows)
            cursor.close()
            df.rename(columns={0: "Date", 1: "Day", 2: "Location", 3: "Staff",
                      4: "Receipt#", 5: "Coordinator", 6: "Clients"}, inplace=True)
            st.table(df.astype(str))

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


def showPrevNextButton(id: Str):
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
