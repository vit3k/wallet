import streamlit as st
import bonds
import pandas as pd
import stocks
import account
from account_chart import account_chart

st.set_page_config(layout="wide")

bondsData = bonds.get_bonds_data()
stocksData = stocks.get_stocks_data()

bondsAgg = pd.DataFrame(bondsData[["count", "value", "current_value", "gain"]].aggregate('sum')).transpose()
bondsAgg["gain %"] = bondsAgg["gain"] / bondsAgg["value"] * 100

stocksAgg = stocksData.groupby("ticker")[["count", "value_pln", "current_value_pln", "gain_pln"]].aggregate("sum")
stocksAgg["gain %"] = stocksAgg["gain_pln"] / stocksAgg["value_pln"] * 100

stockSum = stocksAgg["current_value_pln"].sum()
bondSum = bondsAgg["current_value"].sum()
total = bondSum + stockSum

totalsDf = pd.DataFrame([[bondSum, stockSum, total], [bondSum/total * 100, stockSum/total * 100, 100]], 
                        columns=["Obligacje", "Giełda", "Razem"], index=["Kwoty", "Procenty"])

totalRow =  pd.DataFrame(stocksAgg.sum(), columns=['Total']).transpose()
stocksAgg = pd.concat([stocksAgg, totalRow])
stocksAgg.reset_index(inplace=True)
accountSummary = account.get_account_summary(stocksData, bondsData)

## UI
st.title("Portfel")
st.altair_chart(account_chart(accountSummary), use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.header("Wartość portfela")
    st.dataframe(totalsDf.style.format(precision=2, thousands=' '), use_container_width = True )

with col2:
    st.header("Obligacje - podsumowanie")
    st.dataframe(bondsAgg.style.format(precision=2, thousands=' '), hide_index=True, use_container_width = True )

def gain_color(s):
    if s["index"] == "Total":
        return ['background-color: #005f7e; font-weight: bold']*len(s)
    return ['background-color: #008b4d']*len(s) if s["gain_pln"] > 0 else ['background-color: #cd3a4b']*len(s)

st.header("Giełda")
st.dataframe(stocksAgg.style.format(precision=2, thousands=' ').apply(gain_color, axis = 1), use_container_width = True, hide_index=True )

st.header("Giełda - transakcje")
st.dataframe(stocksData[["account_name", "ticker", "transaction_date", "count", "price", "currency", "value_pln", "current_value_pln", "gain_pln", "gain %"]], use_container_width=True, hide_index=True)

st.header("Obligacje")
bondsData["interest_rate %"] = bondsData["interest_rate"] * 100
bondsData["margin %"] = bondsData["margin"] * 100

st.dataframe(bondsData[["name", "transaction_date", "count", "interest_rate %", "margin %", "current_value", "gain"]], hide_index=True, use_container_width=True)

