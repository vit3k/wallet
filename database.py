import psycopg2
import config
import streamlit as st

@st.cache_resource
def get_database():
    dbc = config.get_config()["database"]

    conn = psycopg2.connect(database=dbc["db"],
                            host=dbc["host"],
                            user=dbc["user"],
                            password=dbc["password"],
                            port=dbc["port"])
    return conn
