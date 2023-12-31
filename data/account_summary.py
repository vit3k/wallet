import pandas as pd
from datetime import date
import yfinance as yf

def get_account_summary(stocks: pd.DataFrame, bonds: pd.DataFrame) -> pd.DataFrame:
    now = date.today()
    
    currencies = stocks.groupby("currency")["transaction_date"].min()

    currenciesDfs = []
    for currency, transaction_date in currencies.items():
        currency_range = pd.DataFrame(pd.date_range(start=transaction_date, end=now), columns=["Date"])
        ticker = "PLN=X" if currency == "USD" else "EURPLN=X"
        currency_range["ticker"] = ticker
        currency_range["currency"] = currency
        currency_range["Date"] = currency_range["Date"].map(lambda d: d.replace(tzinfo=None).date())
        currency_quotes = yf.Ticker(ticker).history(start=transaction_date, end=now)
        currency_quotes.reset_index(inplace=True)
        currency_quotes["Date"] = currency_quotes["Date"].map(lambda d: d.replace(tzinfo=None).date())
        merged_df = pd.merge(left = currency_range, right = currency_quotes[["Date","Close"]], on = "Date", how="left")
        merged_df.ffill(inplace=True)
        currenciesDfs.append(merged_df)

    currency_quotes = pd.concat(currenciesDfs)
    currency_quotes.reset_index(inplace=True)
    currency_quotes.drop("index", axis="columns", inplace=True)
    currency_quotes.drop("ticker", axis="columns", inplace=True)
    currency_quotes.set_index(["Date", "currency"], inplace=True)
    currency_quotes.columns = ["currency_rate"]

    tickers = stocks.groupby("ticker")["transaction_date"].min()
    quotesDfs = []
    for ticker, transaction_date in tickers.items():
        ticker_range = pd.DataFrame(pd.date_range(start=transaction_date, end=now), columns=["Date"])
        ticker_range["ticker"] = ticker
        ticker_range["Date"] = ticker_range["Date"].map(lambda d: d.replace(tzinfo=None).date())
        quotes = yf.Ticker(ticker).history(start=transaction_date, end=now)
        quotes.reset_index(inplace=True)
        quotes["Date"] = quotes["Date"].map(lambda d: d.replace(tzinfo=None).date())
        merged_df = pd.merge(left = ticker_range, right = quotes[["Date","Close"]], on = "Date", how="left")
        merged_df.ffill(inplace=True)
        quotesDfs.append(merged_df)

    quotes = pd.concat(quotesDfs)
    quotes.reset_index(inplace=True)
    quotes.drop("index", axis="columns", inplace=True)

    stocks_grouped = pd.DataFrame(stocks.groupby(["transaction_date", "ticker", "currency"])["count"].sum())
    stocks_grouped.reset_index(inplace=True)

    account_value_df = pd.merge(left = quotes, right = stocks_grouped, left_on=["Date", "ticker"], right_on=["transaction_date", "ticker"], how="left")
    account_value_df["currency"].ffill(inplace=True)
    account_value_df["count"].fillna(0, inplace=True)
    account_value_df.drop("transaction_date", axis="columns", inplace=True)
    account_value_df["count_sum"] = account_value_df.groupby(["ticker"])["count"].cumsum()
    account_value_df["value"] = account_value_df["Close"] * account_value_df["count_sum"]

    account_value_df = pd.merge(left = account_value_df, right = currency_quotes, left_on=["Date", "currency"], right_on = ["Date", "currency"], how="left")
    account_value_df["value_pln"] = account_value_df["value"] * account_value_df["currency_rate"]
    account_value_df = account_value_df[["Date", "ticker", "value_pln"]].copy()
    account_value_df.set_index(["Date", "ticker"], inplace=True)
    account_value_df.sort_index(inplace=True)
    
    bonds_value = []
    for i, val in bonds.iterrows():
        bonds_df = pd.DataFrame(val["history"])
        bonds_df["value_pln"] = bonds_df["value"]
        bonds_df.reset_index(inplace=True)
        bonds_df.drop("value", inplace=True, axis="columns")
        bonds_df.drop("index", inplace=True, axis="columns")
        bonds_value.append(bonds_df)
    
    bonds_value_df = pd.concat(bonds_value)
    bonds_value_df = pd.DataFrame(bonds_value_df.groupby("Date")["value_pln"].sum())
    bonds_value_df["ticker"] = "Bonds"
    bonds_value_df.reset_index(inplace=True)
    bonds_value_df.set_index(["Date", "ticker"], inplace=True)

    account_value_df = pd.concat([account_value_df, bonds_value_df])

    account_value_df.sort_index(inplace=True)
    account_value_df.reset_index(inplace=True)

    return account_value_df