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

@st.cache_data(ttl = 3600)
def get_accounts_money_latest() -> pd.DataFrame:
    money = get_accounts_money()
    money_idxmax = pd.DataFrame(money.groupby(["account_id", "account", "currency"])["created_at"].idxmax())
    money_idxmax.reset_index(inplace=True)
    money_agg = []
    for i, val in money_idxmax.iterrows():
        row = money.iloc[val["created_at"]]
        money_agg.append(row)

    money_agg = pd.DataFrame(money_agg)
    money_agg["currency_ticker"] = money_agg["currency"].map({"EUR": "EURPLN=X", "USD": "PLN=X", "PLN": "PLN"})
    money_agg["current_currency_rate"] = money_agg["currency_ticker"].map(lambda t: yf.Ticker(t).history("1d").iloc[0]["Close"] if t != "PLN" else 1)
    money_agg["value_pln"] = money_agg["value"] * money_agg["current_currency_rate"]

    money_agg = money_agg[["account", "currency", "value", "value_pln"]].copy()

    return money_agg

def get_money_currencies() -> pd.DataFrame:
    money_agg = get_accounts_money_latest()
    money_agg_currency = money_agg.groupby("currency")[["value", "value_pln"]].sum()
    money_agg_currency.reset_index(inplace=True)
    return money_agg_currency

def save_account_value(account_id, value):
    conn = database.get_database()
    cursor = conn.cursor()
    cursor.execute("insert into account_money (account_id, value) values (%s ,%s)", (account_id, value))
    cursor.close()
    conn.commit()
    get_accounts_data.clear()
    get_accounts_money_latest.clear()
    get_accounts_money.clear()
