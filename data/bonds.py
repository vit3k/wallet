import pandas as pd

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import psycopg

def get_infation_data():
    inflation = pd.read_excel("https://stat.gov.pl/download/gfx/portalinformacyjny/pl/defaultstronaopisowa/4741/1/1/miesieczne_wskazniki_cen_towarow_i_uslug_konsumpcyjnych_od_1982_roku.xlsx")
    filtered = inflation[inflation["Sposób prezentacji"] == "Analogiczny miesiąc poprzedniego roku = 100"][["Rok", "Miesiąc", "Wartość"]].copy()
    filtered.columns = ["year", "month", "value"]
    return filtered

def get_bonds_data(conn: psycopg.connection.Connection, inflation_data):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bonds")
    bonds = cursor.fetchall()
    cursor.close()
    bondsDf = pd.DataFrame(bonds)
    bondsDf["value"] = bondsDf.price * bondsDf["count"]
    bondsDf["current_value"] = bondsDf.apply(lambda b: calculate_bond_value(b, inflation_data), axis=1)
    bondsDf["gain"] = bondsDf["current_value"] - bondsDf["value"]
    bondsDf["gain %"] = bondsDf["gain"] / bondsDf["value"] * 100
    bondsDf["history"] = bondsDf.apply(lambda b: calculate_bond_history(b, inflation_data), axis = 1)
    return bondsDf.sort_values("transaction_date", ascending=False)

def calculate_rod_value(rod: pd.Series, inflation_data: pd.DataFrame, now: datetime.date):
    currentValue = rod["value"]
    inflationData = inflation_data
    
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

def calculate_rod_history(rod, inflation_data: pd.DataFrame, now):
    currentValue = rod["value"]
    inflationData = inflation_data
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

def calculate_bond_history(bond, inflation_data, now = datetime.now().date()):
    if bond.type == "ROD":
        return calculate_rod_history(bond, inflation_data, now)
    else:
        raise Exception("Not supported bond type")
    
def calculate_bond_value(bond: pd.Series, inflation_data, now = datetime.now().date()):
    if bond.type == "ROD":
        return calculate_rod_value(bond, inflation_data, now)
    else:
        raise Exception("Not supported bond type")
    
def add_bonds(conn: psycopg.connection.Connection, transaction):
    cursor = conn.cursor()
    cursor.execute("insert into bonds (bond_type, ticker, direction, transaction_date, price, count, interest_rate, margin, early_sell_commision) values (%s, %s ,%s, %s, %s, %s, %s, %s, %s)", 
                   (transaction["bond_type"], transaction["ticker"], transaction["direction"], transaction["transaction_date"], transaction["price"], 
                    transaction["count"], transaction["interest_rate"], transaction["margin"], transaction["early_sell_commision"]))
    cursor.close()
    conn.commit()