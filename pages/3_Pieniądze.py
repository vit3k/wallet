import streamlit as st
import data
import pandas as pd

st.set_page_config(layout="wide")

money_latest = data.get_accounts_money_latest()
money_total = money_latest["value_pln"].sum()
money_total_row =  pd.DataFrame({"account": ["Total"], "currency": [""], "value": [""], "value_pln": [money_total]})
money_latest = pd.concat([money_latest, money_total_row], ignore_index=True)

def money_color(s):
    if s["account"] == "Total":
        return ['background-color: #005f7e; font-weight: bold']*len(s)
    return ['']*len(s)

st.header("Pieniądze")
st.dataframe(money_latest.style.format(precision=2, thousands=' ').apply(money_color, axis = 1), hide_index=True, use_container_width = True )