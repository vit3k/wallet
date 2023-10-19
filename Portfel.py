import streamlit as st
import bonds
import pandas as pd
import stocks
import account
from account_chart import account_chart
import data

st.set_page_config(layout="wide")

bondsData = bonds.get_bonds_data()
stocksData = stocks.get_stocks_data()
money_latest = data.get_accounts_money_latest()

currencies_df = data.get_money_currencies()
currencies_total_row =  pd.DataFrame({"currency": ["Total"], "value": [""], "value_pln": [currencies_df["value_pln"].sum()]})
currencies_df = pd.concat([currencies_df, currencies_total_row], ignore_index=True)

money_total = money_latest["value_pln"].sum()

bondsAgg = pd.DataFrame(bondsData[["count", "value", "current_value", "gain"]].aggregate('sum')).transpose()
bondsAgg["gain %"] = bondsAgg["gain"] / bondsAgg["value"] * 100

stocksAgg = stocksData.groupby("ticker")[["count", "value_pln", "current_value_pln", "gain_pln"]].aggregate("sum")
stocksAgg["gain %"] = stocksAgg["gain_pln"] / stocksAgg["value_pln"] * 100

stockSum = stocksAgg["current_value_pln"].sum()
bondSum = bondsAgg["current_value"].sum()
investements_total = bondSum + stockSum

investments_total_df = pd.DataFrame([[bondSum, stockSum, investements_total], [bondSum/investements_total * 100, stockSum/investements_total * 100, 100]], 
                        columns=["Obligacje", "Giełda", "Razem"], index=["Kwoty", "Procenty"]).transpose()

stocks_total_row =  pd.DataFrame(stocksAgg.sum(), columns=['Total']).transpose()
stocks_total_row["gain %"] = stocks_total_row["gain_pln"] / stocks_total_row["value_pln"] * 100
stocksAgg = pd.concat([stocksAgg, stocks_total_row])
stocksAgg.reset_index(inplace=True)

accountSummary = account.get_account_summary(stocksData, bondsData)

all_total_df = pd.DataFrame([[investements_total, money_total, (investements_total+money_total)], [investements_total/(investements_total+money_total) * 100, money_total/(investements_total+money_total) * 100, 100]], 
                        columns=["Zainwestowane", "Pieniądze", "Razem"], index=["Kwoty", "Procenty"]).transpose()

## UI
st.title("Portfel")

def money_agg_color(s: pd.Series):
    if s["currency"] == "Total":
        return ['background-color: #005f7e; font-weight: bold']*len(s)
    return ['']*len(s)


col1, col2 = st.columns(2)

with col1:
    st.header("Razem")
    st.dataframe(all_total_df.style.format(precision=2, thousands=' '), use_container_width = True )
    
with col2:
    st.header("Pieniądze")
    st.dataframe(currencies_df.style.format(precision=2, thousands=' ').apply(money_agg_color, axis=1), use_container_width = True, hide_index = True)

col3, col4 = st.columns(2)
with col3:
    st.header("Inwestycje")
    st.dataframe(investments_total_df.style.format(precision=2, thousands=' '), use_container_width = True )
    
with col4:
    st.header("Obligacje")
    st.dataframe(bondsAgg.style.format(precision=2, thousands=' '), hide_index=True, use_container_width = True )
    
def gain_color(s):
    if s["index"] == "Total":
        return ['background-color: #005f7e; font-weight: bold']*len(s)
    return ['background-color: #008b4d']*len(s) if s["gain_pln"] > 0 else ['background-color: #cd3a4b']*len(s)

st.header("Giełda")
st.dataframe(stocksAgg.style.format(precision=2, thousands=' ').apply(gain_color, axis = 1), use_container_width = True, hide_index=True )

st.header("Wykres")
# st.dataframe(accountSummary, use_container_width=True)
st.altair_chart(account_chart(accountSummary), use_container_width=True)
