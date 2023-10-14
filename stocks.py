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
    cursor.execute("SELECT s.*, a.name as account_name, ss.price source_price, ss.currency_rate as source_currency_rate FROM stocks s join accounts a on a.id = s.account_id left join stocks ss on ss.id = s.source_transaction_id")
    stocksResult = cursor.fetchall()
    cursor.close()
    stocks = pd.DataFrame(stocksResult)

    stocks["count"] = stocks.apply(lambda s: s["count"] if s["direction"] == "B" else -s["count"], axis = 1)
    stocks["current_price"] = stocks["ticker"].map(lambda t: yf.Ticker(t).history("1d").iloc[0]["Close"])
    stocks["currency_ticker"] = stocks["currency"].map({"EUR": "EURPLN=X", "USD": "PLN=X"})
    stocks["current_currency_rate"] = stocks["currency_ticker"].map(lambda t: yf.Ticker(t).history("1d").iloc[0]["Close"])
    
    stocks["value_pln"] = stocks.apply(lambda s: 
                                       (
                                           (s["source_price"] if s["direction"] == "S" else s["price"]) * 
                                           s["count"] * 
                                           (s["source_currency_rate"] if s["direction"]=="S" else s["currency_rate"])
                                           ), axis = 1)
    stocks["current_value_pln"] = stocks.apply(lambda s: (s["current_price"] * s["count"] * s["current_currency_rate"]), axis = 1)
    stocks["gain_pln"] = stocks["current_value_pln"] - stocks["value_pln"]
    stocks["gain %"] = stocks["gain_pln"] / stocks["value_pln"] * 100
    
    if stocks["direction"] == "S" and stocks["source_transaction_id"] is None:
        pass # do something when sell in FIFO manner
    
    #print(stocks.groupby("ticker")["transaction_date"].min())
    return stocks.sort_values("transaction_date", ascending=False)

