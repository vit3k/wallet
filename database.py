import streamlit as st
import data.database

@st.cache_resource
def get_database():
    return data.database.get_database(st.secrets.database_connection_string)
