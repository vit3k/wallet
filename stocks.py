import yfinance as yf
import streamlit as st
import database
import psycopg2.extras
import pandas as pd



def get_current_quote(ticker):
    yf.Ticker(ticker).history("1d").iloc[0]["Close"]

def get_stock_history(t):
    pass

@st.cache_data(ttl = 3600)
def get_stocks_data():
    conn = database.get_database()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT s.*, a.name as account_name FROM stocks s join accounts a on a.id = s.account_id")
    stocksResult = cursor.fetchall()
    cursor.close()
    stocks = pd.DataFrame(stocksResult)

    stocks["count"] = stocks.apply(lambda s: s["count"] if s["direction"] == "B" else -s["count"], axis = 1)
    stocks["current_price"] = stocks["ticker"].map(lambda t: yf.Ticker(t).history("1d").iloc[0]["Close"])
    stocks["currency_ticker"] = stocks["currency"].map({"EUR": "EURPLN=X", "USD": "PLN=X"})
    stocks["current_currency_rate"] = stocks["currency_ticker"].map(lambda t: yf.Ticker(t).history("1d").iloc[0]["Close"])

    stocks["value_pln"] = stocks.apply(lambda s: (s["price"] * s["count"] * s["currency_rate"]) if s["direction"] == "B" else 0, axis = 1)
    stocks["current_value_pln"] = stocks.apply(lambda s: (s["current_price"] * s["count"] * s["current_currency_rate"]) if s["direction"] == "B" else 0, axis = 1)
    stocks["gain_pln"] = stocks["current_value_pln"] - stocks["value_pln"]
    stocks["gain %"] = stocks["gain_pln"] / stocks["value_pln"] * 100
    
    #print(stocks.groupby("ticker")["transaction_date"].min())
    return stocks.sort_values("transaction_date", ascending=False)

