import pandas as pd
import streamlit as st
import database
import psycopg2.extras 
from datetime import datetime, timedelta
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
    bondsDf["gain %"] = bondsDf["gain"] / bondsDf["value"] * 100
    bondsDf["history"] = bondsDf.apply(calculate_bond_history, axis = 1)
    return bondsDf.sort_values("transaction_date", ascending=False)

@st.cache_data(ttl = 3600)
def get_infation_data():
    inflation = pd.read_excel("https://stat.gov.pl/download/gfx/portalinformacyjny/pl/defaultstronaopisowa/4741/1/1/miesieczne_wskazniki_cen_towarow_i_uslug_konsumpcyjnych_od_1982_roku.xlsx")
    filtered = inflation[inflation["Sposób prezentacji"] == "Analogiczny miesiąc poprzedniego roku = 100"][["Rok", "Miesiąc", "Wartość"]].copy()
    filtered.columns = ["year", "month", "value"]
    return filtered

def calculate_rod_value(rod: pd.Series, now: datetime.date):
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

def calculate_rod_history(rod, now):
    currentValue = rod["value"]
    inflationData = get_infation_data()
    history = [{"ticker": rod["name"],"Date": rod.transaction_date, "value": currentValue}]
    for i in range(0, 12):
        valueInPeriod = 0
        periodStart = rod.transaction_date + relativedelta(years=i)
        if periodStart > now:
            break
        interestRate = rod.interest_rate
        if i != 0:
            inflationPeriod = periodStart - relativedelta(months=2)
            inflationRate = (inflationData[(inflationData.year == inflationPeriod.year) & (inflationData.month == inflationPeriod.month)].iloc[0]["value"] - 100) / 100
            interestRate = max(inflationRate, 0) + rod.margin

        periodEnd = periodStart + relativedelta(years=1)
        numberOfDays = (periodEnd - periodStart).days

        if now < periodEnd:
            periodEnd = now
        interestRatePerDay = interestRate / numberOfDays

        res_date = periodStart + relativedelta(days=1)
        while res_date <= periodEnd:
            days = (res_date - periodStart).days
            valueInPeriod = currentValue * days * interestRatePerDay
            history.append({"ticker": rod["name"],"Date": res_date, "value": (currentValue + valueInPeriod)})
            res_date += relativedelta(days=1)

        currentValue += valueInPeriod
        
    return history

def calculate_bond_history(bond, now = datetime.now().date()):
    if bond.type == "ROD":
        return calculate_rod_history(bond, now)
    else:
        raise Exception("Not supported bond type")
    
def calculate_bond_value(bond: pd.Series, now = datetime.now().date()):
    if bond.type == "ROD":
        return calculate_rod_value(bond, now)
    else:
        raise Exception("Not supported bond type")