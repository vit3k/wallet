import streamlit as st
import time
import data
import pandas as pd

st.set_page_config(layout="wide")

accounts = pd.DataFrame(data.get_accounts_data())

def account_id_to_name(id):
    return accounts[accounts["id"] == id].iloc[0]["name"]

def stock_form():
    direction = st.selectbox("Rodzaj transakcji", ["Zakup", "Sprzedaz"])
    ticker = st.text_input("Ticker")
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

st.header("Dodaj transakcje")

instrument_type = st.selectbox("Typ instrumentu", ["Giełda", "Obligacje"])

match instrument_type:
    case "Giełda":
        stock_form()
    case _:
        st.error("Not supported")

