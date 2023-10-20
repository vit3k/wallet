import streamlit as st
import data
import pandas as pd

st.set_page_config(layout="wide")

if 'show_form' not in st.session_state:
    st.session_state.show_form = False

def show_form():
    st.session_state.show_form = not st.session_state.show_form

money_latest = data.get_accounts_money_latest()
money_total = money_latest["value_pln"].sum()
money_total_row =  pd.DataFrame({"account": ["Total"], "currency": [""], "value": [""], "value_pln": [money_total]})
money_latest = pd.concat([money_latest, money_total_row], ignore_index=True)

def money_color(s):
    if s["account"] == "Total":
        return ['background-color: #005f7e; font-weight: bold']*len(s)
    return ['']*len(s)

accounts = pd.DataFrame(data.get_accounts_data())

def account_id_to_name(id):
    return accounts[accounts["id"] == id].iloc[0]["name"]

st.header("Pieniądze")
st.button("Zaktualizuj konto", on_click=show_form)
if st.session_state.show_form:
    account = st.selectbox("Konto", accounts["id"], format_func=account_id_to_name)
    value = st.number_input("Wartość")
    submit = st.button("Zapisz")
    if submit:
        with st.spinner("Zapisuję"):
            data.save_account_value(account, value)
        st.success("Zapisano")
        st.session_state.show_form = False
        st.rerun()

st.dataframe(money_latest.style.format(precision=2, thousands=' ').apply(money_color, axis = 1), hide_index=True, use_container_width = True )