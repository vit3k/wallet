import psycopg
from psycopg.rows import dict_row

def get_database(connection_string: str):

    conn = psycopg.connect(connection_string, row_factory=dict_row)
    
    return conn
