import altair as alt
import data.stocks
import data.bonds
import data.account_summary
import data.database
from datetime import datetime

db = data.database.get_database("user=postgres password=jufFo2-xycgyn-viqmam host=db.cfwhcubsayehudtvrfxk.supabase.co port=5432 dbname=postgres")

inflation_data = data.bonds.get_infation_data()
chart_data = data.account_summary.get_account_summary(data.stocks.get_stocks_data(db), data.bonds.get_bonds_data(db, inflation_data))
chart_data["Date"] = chart_data["Date"].map(lambda d: datetime.combine(d, datetime.min.time()))
line = alt.Chart(chart_data).mark_line(clip=True).encode(
            x=alt.X("Date:T").scale(alt.Scale(domain=["2023-01-01", "2023-12-31"])),
            y=alt.Y("value_pln"),
            color="ticker"
            #tooltip=["Date", "value_pln"]
        )
line