import pandas as pd

import psycopg2



def import_stocks():
    stocks = pd.read_excel("/Users/witek/Downloads/Pieniądze.xlsx", "Giełda")
    stocks["Ticker"] = stocks["Ticker"].map({
        "FRA:IUSQ": "IUSQ.DE", "NASDAQ:INTC": "INTC", "LON:ISAC": "ISAC.L"
    })
    cur = conn.cursor()
    for index, row in stocks.iterrows():
        cur.execute("INSERT INTO public.stocks (ticker, direction, transaction_date,price,currency, currency_rate,brokerage,count) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (row["Ticker"], "B", row["Data zakupu"], row["Cena"], row["Waluta inst."], row["Kurs waluty"], row["Prowizja"], row["Liczba"]))
        
    conn.commit()
    cur.close()
        

def import_bonds():
    bonds = pd.read_excel("/Users/witek/Downloads/Pieniądze.xlsx", "Obligacje")
    cur = conn.cursor()
    for index, row in bonds.iterrows():
        cur.execute("INSERT INTO bonds (name, type, direction, transaction_date, count, price, interest_rate, margin, early_sell_commision) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (row["Obligacje"], "ROD", "B", row["Data zakupu"], row["Liczba"], row["Cena"], row["Oprocentowanie1"], row["Marża"], row["Koszt wcz. wyk."]))
        
    conn.commit()
    cur.close() 

def import_money():
    pass

#import_stocks()
import_bonds()
