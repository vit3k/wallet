import yfinance as yf
import streamlit as st
import database
import psycopg2.extras
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
from datetime import datetime

def get_current_quote(ticker):
    yf.Ticker(ticker).history("1d").iloc[0]["Close"]

def get_stock_history(t):
    pass

@st.cache_data(ttl = 3600)
def get_quote(ticker: str) -> float:
    return yf.Ticker(ticker).history("1d").iloc[0]["Close"]

def calculate_values(s: pd.Series, stocks: pd.DataFrame):
    value_pln = 0
    if s["direction"] == "S":
        s["count"] = -s["count"]
        if s["source_transaction_id"] is not None:
            price = s["source_price"]
            currency_rate = s["source_currency_rate"]
            s["value_pln"] =  price * s["count"] * currency_rate
        else:
            # calculate source in FIFO manner
            buys = stocks[(stocks["ticker"] == s["ticker"]) and (stocks["direction"] == "B")]
            buys.sort_values("transaction_date", ascending=True, inplace=True)
            # TODO: finish but this can happen only on IKE/IKZE for now so low priority
            pass
    else:
        price = s["price"]
        currency_rate = s["currency_rate"]
        s["value_pln"] =  price * s["count"] * currency_rate

    
    
    return s

@st.cache_data(ttl = 3600)
def get_stocks_data():
    conn = database.get_database()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT s.*, a.name as account_name, ss.price source_price, ss.currency_rate as source_currency_rate FROM stocks s join accounts a on a.id = s.account_id left join stocks ss on ss.id = s.source_transaction_id")
    stocksResult = cursor.fetchall()
    cursor.close()
    stocks = pd.DataFrame(stocksResult)

    stocks["current_price"] = stocks["ticker"].map(get_quote)
    stocks["currency_ticker"] = stocks["currency"].map({"EUR": "EURPLN=X", "USD": "PLN=X"})
    stocks["current_currency_rate"] = stocks["currency_ticker"].map(lambda t: yf.Ticker(t).history("1d").iloc[0]["Close"])
    
    stocks = stocks.apply(lambda s: calculate_values(s, stocks), axis = 1)
    stocks["current_value_pln"] = stocks["current_price"] * stocks["current_currency_rate"] * stocks["count"]
    stocks["gain_pln"] = stocks["current_value_pln"] - stocks["value_pln"]
    stocks["gain %"] = stocks["gain_pln"] / stocks["value_pln"] * 100

    return stocks.sort_values("transaction_date", ascending=False)

@st.cache_data(ttl = 3600)
def get_tickers(time_delta: relativedelta) -> np.ndarray:
    stocks = get_stocks_data()
    date = datetime.now() - time_delta
    return stocks[stocks["transaction_date"] ]["ticker"].unique()


