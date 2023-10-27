import pandas as pd
import yfinance as yf
import psycopg

def get_accounts_data(conn: psycopg.connection.Connection):
    cursor = conn.cursor()
    cursor.execute("SELECT * from accounts")
    accounts = cursor.fetchall()
    cursor.close()
    return accounts

def get_accounts_money(conn: psycopg.connection.Connection) -> pd.DataFrame:
    cursor = conn.cursor()
    cursor.execute("SELECT am.*, a.name as account, a.currency as currency from account_money am join accounts a on a.id = am.account_id")
    accounts = cursor.fetchall()
    cursor.close()
    accounts = pd.DataFrame(accounts)

    return accounts

def get_accounts_money_latest(conn: psycopg.connection.Connection) -> pd.DataFrame:
    money = get_accounts_money(conn)
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

    money_agg = money_agg[["account", "currency", "value", "value_pln", "created_at"]].copy()

    return money_agg

def get_money_currencies(conn: psycopg.connection.Connection) -> pd.DataFrame:
    money_agg = get_accounts_money_latest(conn)
    money_agg_currency = money_agg.groupby("currency")[["value", "value_pln"]].sum()
    money_agg_currency.reset_index(inplace=True)
    return money_agg_currency

def save_account_value(conn: psycopg.connection.Connection, account_id, value):
    cursor = conn.cursor()
    cursor.execute("insert into account_money (account_id, value) values (%s ,%s)", (account_id, value))
    cursor.close()
    conn.commit()

