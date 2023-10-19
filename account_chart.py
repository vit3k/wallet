import altair as alt
import streamlit as st
import pandas as pd

def account_chart(chart_data: pd.DataFrame) -> alt.Chart:
    
    nearest = alt.selection_point(nearest=True, on='mouseover', empty=False,
                                fields=['Date'])
    # x_min = pd.Timestamp(chart_data["Date"].min()).timestamp()
    # x_max = pd.Timestamp(chart_data["Date"].max()).timestamp()
    # print(x_min, x_max)
    line = alt.Chart(chart_data).mark_line().encode(
                x=alt.X("Date", timeUnit='yearmonthdate'),#, scale = alt.Scale(domain=[x_min, x_max])),
                y=alt.Y("value_pln"),
                color="ticker"
                #tooltip=["Date", "value_pln"]
            )

    selectors = alt.Chart(chart_data).mark_point().encode(
        x='Date',
        opacity=alt.value(0),
        tooltip=["Date", alt.Tooltip('value_pln', format=',.2f')]
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
    return chart
    #st.altair_chart(chart, use_container_width=True)