import streamlit as st
import bonds
import pandas as pd
import stocks
import account
from account_chart import account_chart
import data
import yfinance as yf

st.set_page_config(layout="wide")

bondsData = bonds.get_bonds_data()
stocksData = stocks.get_stocks_data()
money = data.get_accounts_money()

money_idxmax = pd.DataFrame(money.groupby(["account_id", "account", "currency"])["created_at"].idxmax())
money_idxmax.reset_index(inplace=True)
money_agg = []
for i, val in money_idxmax.iterrows():
    row = money.iloc[val["created_at"]]
    money_agg.append(row)

money_agg = pd.DataFrame(money_agg)
money_agg["currency_ticker"] = money_agg["currency"].map({"EUR": "EURPLN=X", "USD": "PLN=X", "PLN": "PLN"})
money_agg["current_currency_rate"] = money_agg["currency_ticker"].map(lambda t: yf.Ticker(t).history("1d").iloc[0]["Close"] if t != "PLN" else 1)
money_agg["value_pln"] = money_agg["value"] * money_agg["current_currency_rate"]

money_agg = money_agg[["account", "currency", "value", "value_pln"]].copy()
#print(money_agg)

money_agg_currency = money_agg.groupby("currency")[["value", "value_pln"]].sum()
money_agg_currency.reset_index(inplace=True)
money_agg_currency_total =  pd.DataFrame({"currency": ["Total"], "value": [""], "value_pln": [money_agg_currency["value_pln"].sum()]})

money_agg_currency = pd.concat([money_agg_currency, money_agg_currency_total], ignore_index=True)

money_total = money_agg["value_pln"].sum()
money_total_row =  pd.DataFrame({"account": ["Total"], "currency": [""], "value": [""], "value_pln": [money_total]})

money_agg = pd.concat([money_agg, money_total_row], ignore_index=True)

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
totalRow["gain %"] = totalRow["gain_pln"] / totalRow["value_pln"] * 100
stocksAgg = pd.concat([stocksAgg, totalRow])
stocksAgg.reset_index(inplace=True)
accountSummary = account.get_account_summary(stocksData, bondsData)


totals = pd.DataFrame([[total, money_total, (total+money_total)], [total/(total+money_total) * 100, money_total/(total+money_total) * 100, 100]], 
                        columns=["Zainwestowane", "Pieniądze", "Razem"], index=["Kwoty", "Procenty"])

## UI
st.title("Portfel")

def money_agg_color(s: pd.Series):
    print(s)
    if s["currency"] == "Total":
        return ['background-color: #005f7e; font-weight: bold']*len(s)
    return ['']*len(s)

def money_color(s):
    if s["account"] == "Total":
        return ['background-color: #005f7e; font-weight: bold']*len(s)
    return ['']*len(s)

col1, col2 = st.columns(2)

with col1:
    st.header("Wartość portfela")
    st.dataframe(totalsDf.style.format(precision=2, thousands=' '), use_container_width = True )

with col2:
    st.header("Zasoby")
    st.dataframe(totals.style.format(precision=2, thousands=' '), use_container_width = True )

col3, col4 = st.columns(2)
with col3:
    st.header("Obligacje - podsumowanie")
    st.dataframe(bondsAgg.style.format(precision=2, thousands=' '), hide_index=True, use_container_width = True )
with col4:
    st.header("Pieniądze")
    st.dataframe(money_agg_currency.style.format(precision=2, thousands=' ').apply(money_agg_color, axis=1), use_container_width = True, hide_index = True)

def gain_color(s):
    if s["index"] == "Total":
        return ['background-color: #005f7e; font-weight: bold']*len(s)
    return ['background-color: #008b4d']*len(s) if s["gain_pln"] > 0 else ['background-color: #cd3a4b']*len(s)

st.header("Giełda")
st.dataframe(stocksAgg.style.format(precision=2, thousands=' ').apply(gain_color, axis = 1), use_container_width = True, hide_index=True )

st.header("Pieniądze")


st.dataframe(money_agg.style.format(precision=2, thousands=' ').apply(money_color, axis = 1), hide_index=True, use_container_width = True )

st.header("Wykres")
st.altair_chart(account_chart(accountSummary), use_container_width=True)
