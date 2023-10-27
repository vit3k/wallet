import streamlit as st
import cached_data as data

st.set_page_config(layout="wide")

stocksData = data.get_stocks_data()

st.header("Giełda - transakcje")
st.dataframe(stocksData[["account_name", "ticker", "transaction_date", "count", "price", "currency", "value_pln", "current_value_pln", "gain_pln", "gain %"]].style.format(precision=2, thousands=' '), use_container_width=True, hide_index=True)
