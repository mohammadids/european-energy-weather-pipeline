import os
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.analysis.anomaly_detection import detect_daily_anomalies


st.set_page_config(
    page_title="European Energy and Weather Analytics",
    page_icon="",
    layout="wide",
)

COUNTRY_LABELS = {
    "DE_LU": "Germany/Luxembourg",
    "ES": "Spain",
    "FR": "France",
    "IT": "Italy",
}

database_url = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://mohammad:mohammad_password@postgres:5432/energy_weather",
)


@st.cache_resource
def get_engine():
    return create_engine(database_url)


@st.cache_data(ttl=300)
def load_daily_data():
    query = text(
        """
        SELECT *
        FROM mart_daily_country_energy_weather
        ORDER BY date, country_code
        """
    )
    return pd.read_sql(query, get_engine())


@st.cache_data(ttl=300)
def load_table_metrics():
    query = text(
        """
        SELECT 'Weather hourly' AS dataset, COUNT(*) AS rows, MIN(timestamp_utc) AS min_ts, MAX(timestamp_utc) AS max_ts
        FROM fact_weather_hourly
        UNION ALL
        SELECT 'Load hourly', COUNT(*), MIN(timestamp_utc), MAX(timestamp_utc)
        FROM fact_energy_load_hourly
        UNION ALL
        SELECT 'Price hourly', COUNT(*), MIN(timestamp_utc), MAX(timestamp_utc)
        FROM fact_energy_price_hourly
        ORDER BY dataset
        """
    )
    return pd.read_sql(query, get_engine())


@st.cache_data(ttl=300)
def load_negative_price_hours():
    query = text(
        """
        SELECT
            country_code,
            COUNT(*) AS negative_price_hours,
            MIN(price_eur_mwh) AS lowest_price_eur_mwh
        FROM fact_energy_price_hourly
        WHERE price_eur_mwh < 0
        GROUP BY country_code
        ORDER BY negative_price_hours DESC
        """
    )
    return pd.read_sql(query, get_engine())


def add_country_labels(df):
    df = df.copy()
    df["country_label"] = df["country_code"].map(COUNTRY_LABELS).fillna(df["country_code"])
    return df


def format_number(value, decimals=0):
    if pd.isna(value):
        return "n/a"
    return f"{value:,.{decimals}f}"


try:
    daily = load_daily_data()
    table_metrics = load_table_metrics()
    negative_price_hours = load_negative_price_hours()
except Exception as exc:
    st.warning("The dashboard is ready, but the database does not have analytics data yet.")
    st.code(str(exc))
    st.stop()

if daily.empty:
    st.info("No analytics data loaded yet. Run the Prefect pipeline first.")
    st.stop()

daily["date"] = pd.to_datetime(daily["date"]).dt.date
daily = add_country_labels(daily)

min_date = daily["date"].min()
max_date = daily["date"].max()
country_options = sorted(daily["country_label"].unique())

with st.sidebar:
    st.header("Filters")
    selected_countries = st.multiselect(
        "Countries",
        country_options,
        default=country_options,
    )
    selected_dates = st.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
else:
    start_date, end_date = min_date, max_date

filtered = daily[
    (daily["country_label"].isin(selected_countries))
    & (daily["date"] >= start_date)
    & (daily["date"] <= end_date)
].copy()

if filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

filtered["date"] = pd.to_datetime(filtered["date"])
anomalies = detect_daily_anomalies(filtered)
flagged_anomalies = anomalies[anomalies["is_anomaly"]].sort_values(
    "max_abs_z_score", ascending=False
)
table_metrics["min_ts"] = pd.to_datetime(table_metrics["min_ts"])
table_metrics["max_ts"] = pd.to_datetime(table_metrics["max_ts"])

st.title("European Energy and Weather Analytics")
st.caption("Portfolio project by Mohammad Mohammadi")

date_count = filtered["date"].nunique()
country_count = filtered["country_code"].nunique()
daily_records = len(filtered)
fact_records = int(table_metrics["rows"].sum())
latest_date = filtered["date"].max().date()
avg_price = filtered["avg_price_eur_mwh"].mean()
avg_load = filtered["avg_load_mw"].mean()

metric_columns = st.columns(5)
metric_columns[0].metric("Countries", country_count)
metric_columns[1].metric("Days", date_count)
metric_columns[2].metric("Daily Records", f"{daily_records:,}")
metric_columns[3].metric("Hourly Fact Rows", f"{fact_records:,}")
metric_columns[4].metric("Latest Date", str(latest_date))

tab_overview, tab_demand, tab_prices, tab_comparison, tab_anomalies, tab_quality = st.tabs(
    ["Overview", "Weather and Demand", "Prices", "Country Comparison", "Anomalies", "Data Quality"]
)

with tab_overview:
    left, right = st.columns(2)

    with left:
        st.subheader("Daily Electricity Load")
        load_fig = px.line(
            filtered,
            x="date",
            y="avg_load_mw",
            color="country_label",
            labels={
                "date": "Date",
                "avg_load_mw": "Average load (MW)",
                "country_label": "Country",
            },
            template="plotly_dark",
        )
        load_fig.update_layout(height=390, legend_title_text="")
        st.plotly_chart(load_fig, width="stretch")

    with right:
        st.subheader("Daily Electricity Price")
        price_fig = px.line(
            filtered,
            x="date",
            y="avg_price_eur_mwh",
            color="country_label",
            labels={
                "date": "Date",
                "avg_price_eur_mwh": "Average price (EUR/MWh)",
                "country_label": "Country",
            },
            template="plotly_dark",
        )
        price_fig.update_layout(height=390, legend_title_text="")
        st.plotly_chart(price_fig, width="stretch")

    summary = (
        filtered.groupby("country_label", as_index=False)
        .agg(
            days=("date", "nunique"),
            avg_temperature_c=("avg_temperature_2m", "mean"),
            avg_load_mw=("avg_load_mw", "mean"),
            avg_price_eur_mwh=("avg_price_eur_mwh", "mean"),
            peak_load_mw=("peak_load_mw", "max"),
        )
        .sort_values("country_label")
    )
    st.subheader("Country Summary")
    st.dataframe(
        summary,
        width="stretch",
        hide_index=True,
        column_config={
            "country_label": "Country",
            "days": "Days",
            "avg_temperature_c": st.column_config.NumberColumn("Avg Temp (C)", format="%.2f"),
            "avg_load_mw": st.column_config.NumberColumn("Avg Load (MW)", format="%.2f"),
            "avg_price_eur_mwh": st.column_config.NumberColumn("Avg Price (EUR/MWh)", format="%.2f"),
            "peak_load_mw": st.column_config.NumberColumn("Peak Load (MW)", format="%.2f"),
        },
    )

with tab_demand:
    top_line = st.columns(3)
    top_line[0].metric("Average Load", f"{format_number(avg_load, 0)} MW")
    top_line[1].metric("Average Temperature", f"{format_number(filtered['avg_temperature_2m'].mean(), 2)} C")
    top_line[2].metric("Peak Daily Load", f"{format_number(filtered['peak_load_mw'].max(), 0)} MW")

    demand_fig = px.scatter(
        filtered,
        x="avg_temperature_2m",
        y="avg_load_mw",
        color="country_label",
        size="peak_load_mw",
        hover_data={
            "date": "|%Y-%m-%d",
            "avg_price_eur_mwh": ":.2f",
            "peak_load_mw": ":.0f",
            "country_label": False,
        },
        labels={
            "avg_temperature_2m": "Average temperature (C)",
            "avg_load_mw": "Average load (MW)",
            "country_label": "Country",
            "avg_price_eur_mwh": "Average price (EUR/MWh)",
            "peak_load_mw": "Peak load (MW)",
        },
        template="plotly_dark",
    )
    demand_fig.update_layout(height=520, legend_title_text="")
    st.plotly_chart(demand_fig, width="stretch")

    correlations = (
        filtered.groupby("country_label")
        .apply(lambda group: group["avg_temperature_2m"].corr(group["avg_load_mw"]))
        .reset_index(name="temperature_load_correlation")
        .sort_values("temperature_load_correlation")
    )
    st.subheader("Temperature and Load Correlation")
    st.dataframe(
        correlations,
        width="stretch",
        hide_index=True,
        column_config={
            "country_label": "Country",
            "temperature_load_correlation": st.column_config.NumberColumn("Correlation", format="%.3f"),
        },
    )

with tab_prices:
    price_columns = st.columns(3)
    price_columns[0].metric("Average Price", f"{format_number(avg_price, 2)} EUR/MWh")
    price_columns[1].metric("Highest Daily Price", f"{format_number(filtered['avg_price_eur_mwh'].max(), 2)} EUR/MWh")
    price_columns[2].metric("Lowest Daily Price", f"{format_number(filtered['avg_price_eur_mwh'].min(), 2)} EUR/MWh")

    price_trend_fig = px.line(
        filtered,
        x="date",
        y="avg_price_eur_mwh",
        color="country_label",
        labels={
            "date": "Date",
            "avg_price_eur_mwh": "Average price (EUR/MWh)",
            "country_label": "Country",
        },
        template="plotly_dark",
    )
    price_trend_fig.update_layout(height=430, legend_title_text="")
    st.plotly_chart(price_trend_fig, width="stretch")

    high_price_days = anomalies[anomalies["price_z_score"] >= 2].sort_values(
        ["price_z_score", "avg_price_eur_mwh"], ascending=False
    )
    if high_price_days.empty:
        high_price_days = anomalies.nlargest(10, "avg_price_eur_mwh")

    left, right = st.columns([2, 1])
    with left:
        st.subheader("High-Price Days")
        high_price_fig = px.bar(
            high_price_days,
            x="date",
            y="avg_price_eur_mwh",
            color="country_label",
            labels={
                "date": "Date",
                "avg_price_eur_mwh": "Average price (EUR/MWh)",
                "country_label": "Country",
            },
            template="plotly_dark",
        )
        high_price_fig.update_layout(height=360, legend_title_text="")
        st.plotly_chart(high_price_fig, width="stretch")

    with right:
        st.subheader("Negative Price Hours")
        negative_price_hours = add_country_labels(negative_price_hours)
        st.dataframe(
            negative_price_hours,
            width="stretch",
            hide_index=True,
            column_config={
                "country_code": None,
                "country_label": "Country",
                "negative_price_hours": "Hours",
                "lowest_price_eur_mwh": st.column_config.NumberColumn("Lowest EUR/MWh", format="%.2f"),
            },
        )

with tab_comparison:
    country_summary = (
        filtered.groupby("country_label", as_index=False)
        .agg(
            avg_temperature_c=("avg_temperature_2m", "mean"),
            avg_wind_100m=("avg_wind_speed_100m", "mean"),
            avg_solar_radiation=("avg_shortwave_radiation", "mean"),
            avg_load_mw=("avg_load_mw", "mean"),
            avg_price_eur_mwh=("avg_price_eur_mwh", "mean"),
        )
        .sort_values("country_label")
    )

    comparison_left, comparison_right = st.columns(2)
    with comparison_left:
        load_bar = px.bar(
            country_summary,
            x="country_label",
            y="avg_load_mw",
            color="country_label",
            labels={"country_label": "Country", "avg_load_mw": "Average load (MW)"},
            template="plotly_dark",
        )
        load_bar.update_layout(height=390, showlegend=False)
        st.plotly_chart(load_bar, width="stretch")

    with comparison_right:
        price_bar = px.bar(
            country_summary,
            x="country_label",
            y="avg_price_eur_mwh",
            color="country_label",
            labels={"country_label": "Country", "avg_price_eur_mwh": "Average price (EUR/MWh)"},
            template="plotly_dark",
        )
        price_bar.update_layout(height=390, showlegend=False)
        st.plotly_chart(price_bar, width="stretch")

    weather_compare = country_summary.melt(
        id_vars=["country_label"],
        value_vars=["avg_temperature_c", "avg_wind_100m", "avg_solar_radiation"],
        var_name="indicator",
        value_name="value",
    )
    weather_compare["indicator"] = weather_compare["indicator"].replace(
        {
            "avg_temperature_c": "Temperature (C)",
            "avg_wind_100m": "Wind speed 100m",
            "avg_solar_radiation": "Shortwave radiation",
        }
    )
    weather_fig = px.bar(
        weather_compare,
        x="country_label",
        y="value",
        color="country_label",
        facet_col="indicator",
        labels={"country_label": "Country", "value": "Average", "indicator": "Indicator"},
        template="plotly_dark",
    )
    weather_fig.update_yaxes(matches=None)
    weather_fig.update_layout(height=390, showlegend=False)
    st.plotly_chart(weather_fig, width="stretch")

with tab_anomalies:
    anomaly_columns = st.columns(4)
    anomaly_columns[0].metric("Flagged Days", f"{len(flagged_anomalies):,}")
    anomaly_columns[1].metric("Price Anomalies", f"{int(anomalies['is_price_anomaly'].sum()):,}")
    anomaly_columns[2].metric("Load Anomalies", f"{int(anomalies['is_load_anomaly'].sum()):,}")
    anomaly_columns[3].metric("Threshold", "z-score >= 2")

    st.caption(
        "Anomalies are calculated inside each country, so each market is compared with its own normal range."
    )

    if flagged_anomalies.empty:
        st.info("No daily price or load anomalies were detected for the selected filters.")
    else:
        anomaly_scatter = px.scatter(
            anomalies,
            x="date",
            y="avg_price_eur_mwh",
            color="anomaly_type",
            size="max_abs_z_score",
            hover_data={
                "country_label": True,
                "avg_load_mw": ":.0f",
                "price_z_score": ":.2f",
                "load_z_score": ":.2f",
            },
            labels={
                "date": "Date",
                "avg_price_eur_mwh": "Average price (EUR/MWh)",
                "anomaly_type": "Anomaly type",
                "country_label": "Country",
                "avg_load_mw": "Average load (MW)",
                "price_z_score": "Price z-score",
                "load_z_score": "Load z-score",
            },
            template="plotly_dark",
        )
        anomaly_scatter.update_layout(height=430, legend_title_text="")
        st.plotly_chart(anomaly_scatter, width="stretch")

        st.subheader("Flagged Daily Anomalies")
        st.dataframe(
            flagged_anomalies[
                [
                    "date",
                    "country_label",
                    "anomaly_type",
                    "avg_price_eur_mwh",
                    "avg_load_mw",
                    "price_z_score",
                    "load_z_score",
                    "max_abs_z_score",
                ]
            ],
            width="stretch",
            hide_index=True,
            column_config={
                "date": st.column_config.DateColumn("Date"),
                "country_label": "Country",
                "anomaly_type": "Type",
                "avg_price_eur_mwh": st.column_config.NumberColumn("Avg Price (EUR/MWh)", format="%.2f"),
                "avg_load_mw": st.column_config.NumberColumn("Avg Load (MW)", format="%.0f"),
                "price_z_score": st.column_config.NumberColumn("Price z-score", format="%.2f"),
                "load_z_score": st.column_config.NumberColumn("Load z-score", format="%.2f"),
                "max_abs_z_score": st.column_config.NumberColumn("Max abs z-score", format="%.2f"),
            },
        )

with tab_quality:
    expected_daily_rows = country_count * date_count
    completeness = daily_records / expected_daily_rows if expected_daily_rows else 0
    quality_metrics = st.columns(4)
    quality_metrics[0].metric("Daily Mart Completeness", f"{completeness:.0%}")
    quality_metrics[1].metric("Weather Rows", f"{int(table_metrics.loc[table_metrics['dataset'] == 'Weather hourly', 'rows'].iloc[0]):,}")
    quality_metrics[2].metric("Load Rows", f"{int(table_metrics.loc[table_metrics['dataset'] == 'Load hourly', 'rows'].iloc[0]):,}")
    quality_metrics[3].metric("Price Rows", f"{int(table_metrics.loc[table_metrics['dataset'] == 'Price hourly', 'rows'].iloc[0]):,}")

    st.subheader("Source Table Coverage")
    st.dataframe(
        table_metrics,
        width="stretch",
        hide_index=True,
        column_config={
            "dataset": "Dataset",
            "rows": st.column_config.NumberColumn("Rows", format="%d"),
            "min_ts": st.column_config.DatetimeColumn("First Timestamp"),
            "max_ts": st.column_config.DatetimeColumn("Latest Timestamp"),
        },
    )

    completeness_by_country = (
        filtered.groupby("country_label", as_index=False)
        .agg(
            daily_rows=("date", "count"),
            days=("date", "nunique"),
            load_days=("avg_load_mw", "count"),
            price_days=("avg_price_eur_mwh", "count"),
        )
        .sort_values("country_label")
    )
    st.subheader("Analytics Mart Coverage")
    st.dataframe(
        completeness_by_country,
        width="stretch",
        hide_index=True,
        column_config={
            "country_label": "Country",
            "daily_rows": "Daily Rows",
            "days": "Days",
            "load_days": "Load Days",
            "price_days": "Price Days",
        },
    )
