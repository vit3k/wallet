import pandas as pd
import streamlit as st
import database
import psycopg2.extras 
from datetime import datetime
from dateutil.relativedelta import relativedelta

@st.cache_data(ttl = 3600)
def get_bonds_data():
    conn = database.get_database()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM bonds")
    bonds = cursor.fetchall()
    cursor.close()
    bondsDf = pd.DataFrame(bonds)
    bondsDf["value"] = bondsDf.price * bondsDf["count"]
    bondsDf["current_value"] = bondsDf.apply(calculate_bond_value, axis=1)
    bondsDf["gain"] = bondsDf["current_value"] - bondsDf["value"]
    return bondsDf

@st.cache_data(ttl = 3600)
def get_infation_data():
    inflation = pd.read_excel("https://stat.gov.pl/download/gfx/portalinformacyjny/pl/defaultstronaopisowa/4741/1/1/miesieczne_wskazniki_cen_towarow_i_uslug_konsumpcyjnych_od_1982_roku.xlsx")
    filtered = inflation[inflation["Sposób prezentacji"] == "Analogiczny miesiąc poprzedniego roku = 100"][["Rok", "Miesiąc", "Wartość"]].copy()
    filtered.columns = ["year", "month", "value"]
    return filtered

def calculate_rod_value(rod, now):
    currentValue = rod["value"]
    inflationData = get_infation_data()
    
    for i in range(0, 12):
        periodStart = rod.transaction_date + relativedelta(years=i)
        if periodStart > now:
            break
        interestRate = rod.interest_rate
        if i != 0:
            inflationPeriod = periodStart - relativedelta(months=2)
            inflationRate = (inflationData[(inflationData.year == inflationPeriod.year) & (inflationData.month == inflationPeriod.month)].iloc[0]["value"] - 100) / 100
            interestRate = max(inflationRate, 0) + rod.margin

        periodEnd = periodStart + relativedelta(years=1)
        numberOfDays = 0
        if now > periodEnd:
            numberOfDays = (periodEnd - periodStart).days
        else:
            numberOfDays = (now - periodStart).days
        
        numberOfDaysInPeriod = (periodEnd - periodStart).days
        calculatedInterestRate = interestRate * (numberOfDays / numberOfDaysInPeriod)
        currentValue += (currentValue * calculatedInterestRate)
        currentValue = round(currentValue, 0)
    return currentValue

def calculate_bond_value(bond, now = datetime.now().date()):
    if bond.type == "ROD":
        return calculate_rod_value(bond, now)
    else:
        raise Exception("Not supported bond type")