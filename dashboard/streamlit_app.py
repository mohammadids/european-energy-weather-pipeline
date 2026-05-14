import os

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text


st.set_page_config(
    page_title="European Energy and Weather Analytics",
    page_icon="",
    layout="wide",
)

st.title("European Energy and Weather Analytics")
st.caption("Portfolio project by Mohammad Mohammadi")

database_url = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://mohammad:mohammad_password@postgres:5432/energy_weather",
)


@st.cache_data(ttl=300)
def load_daily_data():
    engine = create_engine(database_url)
    query = text(
        """
        SELECT *
        FROM mart_daily_country_energy_weather
        ORDER BY date, country_code
        """
    )
    return pd.read_sql(query, engine)


try:
    daily = load_daily_data()
except Exception as exc:
    st.warning("The dashboard is ready, but the database does not have analytics data yet.")
    st.code(str(exc))
    st.stop()

if daily.empty:
    st.info("No analytics data loaded yet. Run the Prefect pipeline first.")
    st.stop()

latest_date = daily["date"].max()
countries = daily["country_code"].nunique()
records = len(daily)

col1, col2, col3 = st.columns(3)
col1.metric("Countries", countries)
col2.metric("Daily Records", records)
col3.metric("Latest Date", str(latest_date))

st.subheader("Weather and Electricity Demand")
fig = px.scatter(
    daily,
    x="avg_temperature_2m",
    y="avg_load_mw",
    color="country_code",
    hover_data=["date"],
    labels={
        "avg_temperature_2m": "Average temperature",
        "avg_load_mw": "Average load (MW)",
        "country_code": "Country",
    },
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Daily Electricity Price")
price_fig = px.line(
    daily,
    x="date",
    y="avg_price_eur_mwh",
    color="country_code",
    labels={
        "date": "Date",
        "avg_price_eur_mwh": "Average price (EUR/MWh)",
        "country_code": "Country",
    },
)
st.plotly_chart(price_fig, use_container_width=True)

