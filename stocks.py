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

    stocks["current_price"] = stocks["ticker"].map(lambda t: yf.Ticker(t).history("1d").iloc[0]["Close"])
    stocks["currency_ticker"] = stocks["currency"].map({"EUR": "EURPLN=X", "USD": "PLN=X"})
    stocks["current_currency_rate"] = stocks["currency_ticker"].map(lambda t: yf.Ticker(t).history("1d").iloc[0]["Close"])
    stocks["value_pln"] = stocks["price"] * stocks["count"] * stocks["currency_rate"]
    stocks["current_value_pln"] = stocks["current_price"] * stocks["count"] * stocks["current_currency_rate"]
    stocks["gain_pln"] = stocks["current_value_pln"] - stocks["value_pln"]


    #print(stocks.groupby("ticker")["transaction_date"].min())
    return stocks

