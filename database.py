import psycopg2
import streamlit as st

@st.cache_resource
def get_database():

    conn = psycopg2.connect(database=st.secrets.database_name,
                            host=st.secrets.database_host,
                            user=st.secrets.database_username,
                            password=st.secrets.database_password,
                            port=st.secrets.database_port)
    return conn
