import streamlit as st
import bonds
import pandas as pd
import stocks
import account

st.set_page_config(layout="wide")

bondsData = bonds.get_bonds_data()
stocksData = stocks.get_stocks_data()

bondsAgg = pd.DataFrame(bondsData[["count", "value", "current_value", "gain"]].aggregate('sum')).transpose()
bondsAgg["gain %"] = bondsAgg["gain"] / bondsAgg["value"] * 100

stocksAgg = stocksData.groupby("ticker")[["count", "value_pln", "current_value_pln", "gain_pln"]].aggregate("sum")

stocksPerAccount = stocksData.groupby(["account_id", "account_name"])[["value_pln", "current_value_pln"]].sum()

stockSum = stocksAgg["current_value_pln"].sum()
bondSum = bondsAgg["current_value"].sum()
total = bondSum + stockSum

totalsDf = pd.DataFrame([[bondSum, stockSum, total], [bondSum/total * 100, stockSum/total * 100, 100]], 
                        columns=["Obligacje", "Giełda", "Razem"], index=["Kwoty", "Procenty"])

totalRow =  pd.DataFrame(stocksAgg.sum(), columns=['Total']).transpose()
stocksAgg = pd.concat([stocksAgg, totalRow])

accountSummary = account.get_account_summary(stocksData)
## UI

st.title("Portfel")

col1, col2 = st.columns(2)

with col1:
    st.header("Wartość portfela")
    st.dataframe(totalsDf.style.format(precision=2, thousands=' '), use_container_width = True )

with col2:
    st.header("Obligacje")
    st.dataframe(bondsAgg.style.format(precision=2, thousands=' '), hide_index=True, use_container_width = True )

st.header("Giełda")
st.dataframe(stocksAgg.style.format(precision=2, thousands=' '), use_container_width = True )

st.header("Portfel - wykres")
st.line_chart(accountSummary)

# st.header("Giełda per konto")
# st.dataframe(stocksPerAccount.style.format(precision=2, thousands=' '), use_container_width = True )

# history = yf.Ticker("INTC").history(start="2020-12-01")
# print(history)
# lineChart = px.line(history, x=history.index, y=history["Close"])
# st.plotly_chart(lineChart)
