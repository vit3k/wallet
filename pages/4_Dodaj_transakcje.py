import streamlit as st
import data
import pandas as pd
import stocks
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

st.set_page_config(layout="wide")

accounts = pd.DataFrame(data.get_accounts_data())

def account_id_to_name(id):
    return accounts[accounts["id"] == id].iloc[0]["name"]

def stock_form():
    direction = st.selectbox("Rodzaj transakcji", ["Zakup", "Sprzedaz"])
    tickers = stocks.get_tickers(relativedelta(years=1))
    tickers =np.append(tickers, ["Inny"])
    ticker = st.selectbox("Ticker", tickers)
    if ticker == "Inny":
        ticker = st.text_input("Inny ticker")
    transaction_date = st.date_input("Data transakcji")
    count = st.number_input("Liczba")
    price = st.number_input("Cena")
    currency = st.selectbox("Waluta", ["PLN", "USD", "EUR"])
    currecy_rate = st.number_input("Kurs waluty")
    borkerage = st.number_input("Prowizja")
    account = st.selectbox("Konto", accounts["id"], format_func=account_id_to_name)
    #st.form_submit_button('Dodaj transakcję')
    add_transaction_click = st.button("Dodaj")
    # if add_transaction_click:
    #     with st.spinner("Zapisuję"):
    #         time.sleep(2)
    #     st.success("Zapisano")
    st.write(ticker)

def bonds_form():
    direction = st.selectbox("Rodzaj transakcji", ["Zakup", "Sprzedaz"])
    bond_type = st.selectbox("Rodzaj obligacji", ["ROD"])
    ticker = st.text_input("Nazwa")
    transaction_date = st.date_input("Data transakcji")
    count = st.number_input("Liczba")
    price = st.number_input("Cena", value=(100 if bond_type=="ROD" else None))
    interest_rate = st.number_input("Oprocentowania")
    margin = st.number_input("Marza")
    early_sell_commision = st.number_input("Kara za wczesny wykup", value=(2 if bond_type=="ROD" else None))
    add_transaction_click = st.button("Dodaj")

st.header("Dodaj transakcje")

instrument_type = st.selectbox("Typ instrumentu", ["Giełda", "Obligacje"])

match instrument_type:
    case "Giełda":
        stock_form()
    case "Obligacje":
        bonds_form()
    case _:
        st.error("Not supported")

