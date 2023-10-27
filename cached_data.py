import streamlit as st
import database
import pandas as pd
import data.stocks
import data.bonds
import data.accounts
import data.account_summary
from dateutil.relativedelta import relativedelta
import numpy as np

@st.cache_data(ttl = 3600)
def get_stocks_data():
    conn = database.get_database()
    return data.stocks.get_stocks_data(conn)

@st.cache_data(ttl = 3600)
def get_tickers(days_delta: int) -> np.ndarray:
    conn = database.get_database()
    return data.stocks.get_tickers(conn, days_delta)

def add_transaction(transaction):
    conn = database.get_database()
    data.stocks.add_transaction(conn, transaction)
    get_stocks_data.clear()

@st.cache_data(ttl = 3600)
def get_bonds_data():
    conn = database.get_database()
    return data.bonds.get_bonds_data(conn, get_infation_data())

@st.cache_data(ttl = 3600)
def get_infation_data():
    return data.bonds.get_infation_data()

def add_bonds(transaction):
    conn = database.get_database()
    data.bonds.add_bonds(conn, transaction)
    get_bonds_data.clear()

@st.cache_data(ttl = 3600)
def get_accounts_data():
    conn = database.get_database()
    return data.accounts.get_accounts_data(conn)

@st.cache_data(ttl = 3600)
def get_accounts_money() -> pd.DataFrame:
    conn = database.get_database()
    return data.accounts.get_accounts_money(conn)

@st.cache_data(ttl = 3600)
def get_accounts_money_latest() -> pd.DataFrame:
    conn = database.get_database()
    return data.accounts.get_accounts_money_latest(conn)

@st.cache_data(ttl = 3600)
def get_money_currencies() -> pd.DataFrame:
    conn = database.get_database()
    return data.accounts.get_money_currencies(conn)

def save_account_value(account_id, value):
    conn = database.get_database()
    data.accounts.save_account_value(conn, account_id, value)
    get_accounts_data.clear()
    get_accounts_money_latest.clear()
    get_accounts_money.clear()

@st.cache_data(ttl = 3600)
def get_account_summary(stocks: pd.DataFrame, bonds: pd.DataFrame) -> pd.DataFrame:
    return data.account_summary.get_account_summary(stocks, bonds)