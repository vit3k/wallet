import streamlit as st
import pandas as pd
import cached_data as data
from account_chart import account_chart

st.set_page_config(layout="wide")
bondsData = data.get_bonds_data()

st.header("Obligacje")
bondsData["interest_rate %"] = bondsData["interest_rate"] * 100
bondsData["margin %"] = bondsData["margin"] * 100

st.dataframe(bondsData[["name", "transaction_date", "count", "interest_rate %", "margin %", "current_value", "gain"]], hide_index=True, use_container_width=True)

# st.dataframe(bondsData.tail(1)["history"][0])