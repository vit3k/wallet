import altair as alt
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

def account_chart(chart_data: pd.DataFrame) -> alt.Chart:
    # chart_data["Date"] = chart_data["Date"].map(lambda d: datetime.combine(d, datetime.min.time()))
    nearest = alt.selection_point(nearest=True, on='mouseover', empty=False,
                                fields=['Date'])
    # x_min = pd.Timestamp(chart_data["Date"].min()).isoformat()
    # x_max = pd.Timestamp(chart_data["Date"].max()).isoformat()
    # print(x_min, x_max)
    # domain = ["2021-01-01", "2023-12-31"]
    # print("typ: ", chart_data.dtypes)
    
    line = alt.Chart(chart_data).mark_line().encode(
                x=alt.X("Date:T"),#.scale(alt.Scale(domain=["2023-01-01", "2023-12-31"])),
                y=alt.Y("sum(value_pln)"),#.scale(domain=[100000, 150000]),
                #color="ticker"
                #tooltip=["Date", "value_pln"]
            )

    selectors = alt.Chart(chart_data).mark_point().encode(
        x='Date',
        opacity=alt.value(0),
        tooltip=["Date", alt.Tooltip('sum(value_pln)', format=',.2f')]
    ).add_params(
        nearest
    )
    # # Draw points on the line, and highlight based on selection
    points = line.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )
    # # Draw text labels near the points, and highlight based on selection
    # text = line.mark_text(align='left', dx=5, dy=-5).encode(
    #     text=alt.condition(nearest, 'value_pln', alt.value(' '))
    # )

    rules = alt.Chart(chart_data).mark_rule(color='gray').encode(
        x='Date',
    ).transform_filter(
        nearest
    )
    chart = alt.layer(
        line, selectors, points, rules
    ).interactive()
    #chart = line.interactive()
    #chart.save("chart.html")
    return chart
    #st.altair_chart(chart, use_container_width=True)

def account_chart2(chart_data: pd.DataFrame) -> alt.Chart:
    brush = alt.selection_interval(encodings=['x'])

    base = alt.Chart(chart_data).mark_area().encode(
        x = 'Date:T',
        y = 'sum(value_pln):Q'
    ).properties(
        width=600,
        height=200
    )

    upper = base.encode(alt.X('date:T').scale(domain=brush))

    lower = base.properties(
        height=60
    ).add_params(brush)

    return alt.vconcat(upper, lower)

def plotly_chart(data: pd.DataFrame):
    fig = px.line(data, x='Date', y="value_pln", color="ticker")
    fig.update_layout(
        width = 800,
        height = 500,
        title = "fixed-ratio axes"
    )
    # fig.update_xaxes(
    #     scaleanchor = "x",
    #     scaleratio = 1,
    # )
    
    return fig