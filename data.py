import streamlit as st
import database
import psycopg2.extras 
import pandas as pd
import yfinance as yf

@st.cache_data(ttl = 3600)
def get_accounts_data():
    conn = database.get_database()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * from accounts")
    accounts = cursor.fetchall()
    cursor.close()
    return accounts

@st.cache_data(ttl = 3600)
def get_accounts_money() -> pd.DataFrame:
    conn = database.get_database()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT am.*, a.name as account, a.currency as currency from account_money am join accounts a on a.id = am.account_id")
    accounts = cursor.fetchall()
    cursor.close()
    accounts = pd.DataFrame(accounts)

    return accounts