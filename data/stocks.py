import yfinance as yf
import streamlit as st
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
from datetime import datetime
import psycopg

def get_current_quote(ticker):
    yf.Ticker(ticker).history("1d").iloc[0]["Close"]

def get_stock_history(t):
    pass

def get_quote(ticker: str) -> float:
    return yf.Ticker(ticker).history("1d").iloc[0]["Close"]

def calculate_values(s: pd.Series, stocks: pd.DataFrame):
    value_pln = 0
    if s["direction"] == "S":
        s["count"] = -s["count"]
        if s["source_transaction_id"] is not None:
            price = s["source_price"]
            currency_rate = s["source_currency_rate"]
            s["value"] = price * s["count"]
            s["value_pln"] =  s["value"] * currency_rate
        else:
            # calculate source in FIFO manner
            buys = stocks[(stocks["ticker"] == s["ticker"]) and (stocks["direction"] == "B")]
            buys.sort_values("transaction_date", ascending=True, inplace=True)
            # TODO: finish but this can happen only on IKE/IKZE for now so low priority
            pass
    else:
        price = s["price"]
        currency_rate = s["currency_rate"]
        s["value"] = price * s["count"]
        s["value_pln"] =  s["value"] * currency_rate
    return s

def get_stocks_data(conn: psycopg.connection.Connection):
    curr = conn.execute("SELECT s.*, a.name as account_name, ss.price source_price, ss.currency_rate as source_currency_rate FROM stocks s join accounts a on a.id = s.account_id left join stocks ss on ss.id = s.source_transaction_id")
    stocksResult = curr.fetchall()
    stocks = pd.DataFrame(stocksResult)

    # quotes = []
    # tickers = stocks["ticker"].unique()
    # for ticker in tickers:


    stocks["current_price"] = stocks["ticker"].map(get_quote)
    stocks["currency_ticker"] = stocks["currency"].map({"EUR": "EURPLN=X", "USD": "PLN=X", "PLN": "PLN"})
    stocks["current_currency_rate"] = stocks["currency_ticker"].map(lambda t: 1 if t == "PLN" else yf.Ticker(t).history("1d").iloc[0]["Close"])
    
    
    stocks = stocks.apply(lambda s: calculate_values(s, stocks), axis = 1)
    stocks["current_value"] = stocks["current_price"] * stocks["count"]
    stocks["gain"] = stocks["current_value"] - stocks["value"]
    stocks["current_value_pln"] = stocks["current_value"] * stocks["current_currency_rate"]
    stocks["gain_pln"] = stocks["current_value_pln"] - stocks["value_pln"]
    stocks["gain %"] = stocks["gain_pln"] / stocks["value_pln"] * 100

    return stocks.sort_values("transaction_date", ascending=False)

def get_tickers(conn: psycopg.connection.Connection, days_delta: int) -> np.ndarray:
    stocks = get_stocks_data(conn)
    date = datetime.now() - relativedelta(days=days_delta)
    return stocks[stocks["transaction_date"] > date.date()]["ticker"].unique()

def add_transaction(conn: psycopg.connection.Connection, transaction):
    cursor = conn.cursor()
    cursor.execute("insert into stocks (ticker, direction, transaction_date, price, currency, currency_rate, brokerage, count, account_id) values (%s ,%s, %s, %s, %s, %s, %s, %s, %s)", 
                   (transaction["ticker"], transaction["direction"], transaction["transaction_date"], transaction["price"], 
                    transaction["currency"], transaction["currency_rate"], transaction["brokerage"], transaction["count"], 
                    transaction["account_id"]))
    cursor.close()
    conn.commit()
    get_stocks_data.clear()


