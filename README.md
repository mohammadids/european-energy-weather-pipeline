# End-to-End Data Pipeline for European Energy and Weather Analytics

Author: **Mohammad Mohammadi**

Status: **In progress**

## Current Milestone

The current working milestone is live weather extraction from the Open-Meteo API. This proves that the project can collect real public API data before the PostgreSQL and ENTSO-E layers are completed.

## Project Summary

I am Mohammad Mohammadi, a Bachelor student in Data Analytics in Italy. In this project, I am building an end-to-end data engineering pipeline that collects European weather and electricity market data from public APIs, stores it in PostgreSQL, validates data quality, automates ETL jobs, and visualizes insights in an interactive dashboard.

The project studies how weather conditions such as temperature, wind speed, and solar radiation relate to electricity demand, renewable generation, and electricity prices across selected European countries.

## Real-World Problem

Electricity systems are increasingly affected by weather. Cold days increase heating demand, hot days increase cooling demand, wind affects wind generation, and solar radiation affects solar production. Analysts and grid stakeholders need reliable pipelines that connect weather data with energy-market indicators.

This project answers the question:

> How do weather conditions affect electricity demand, renewable generation, and electricity prices across selected European countries?

## Planned Data Sources

- **Open-Meteo Historical Weather API** for hourly weather variables.
- **ENTSO-E Transparency Platform** for electricity load, prices, and generation data.
- **Eurostat Energy Data** for optional country-level energy context.
- **Terna Data Portal** as an optional Italy-focused extension.

## Tech Stack

- Python
- SQL
- PostgreSQL
- Public APIs
- Prefect for ETL orchestration
- Pandas and SQLAlchemy
- Data validation with Pandera
- Streamlit and Plotly for dashboarding
- Docker and Docker Compose
- GitHub documentation

## Architecture

```text
Open-Meteo API / ENTSO-E API / Eurostat API
        |
        v
Python extraction scripts
        |
        v
Raw and cleaned data processing
        |
        v
PostgreSQL staging and fact tables
        |
        v
Data validation checks
        |
        v
Prefect ETL orchestration
        |
        v
Analytics marts in PostgreSQL
        |
        v
Streamlit dashboard and SQL analysis
```

## Repository Structure

```text
.
├── README.md
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── docs/
│   ├── architecture.md
│   └── data_dictionary.md
├── sql/
│   ├── 01_schema.sql
│   └── 02_example_queries.sql
├── src/
│   ├── config.py
│   ├── extract/
│   ├── transform/
│   ├── load/
│   ├── validation/
│   └── pipeline/
├── dashboard/
│   └── streamlit_app.py
├── notebooks/
├── tests/
└── data/
    ├── raw/
    └── processed/
```

## Implementation Plan

1. Build weather extraction from Open-Meteo.
2. Create PostgreSQL schema for weather and energy analytics.
3. Load cleaned weather data into PostgreSQL.
4. Add ENTSO-E electricity demand and price extraction.
5. Add data quality checks for duplicates, nulls, freshness, and valid ranges.
6. Orchestrate the pipeline with Prefect.
7. Build SQL analytics marts.
8. Create a Streamlit dashboard.
9. Add forecasting or anomaly detection as an optional extension.
10. Document project results, screenshots, and metrics.

## Dashboard Plan

The dashboard will include:

- Overview of countries, records, freshness, and pipeline runs.
- Weather vs electricity demand trends.
- Country and city comparison.
- Renewable generation and weather indicators.
- Electricity price trends and negative-price hours.
- Data quality and anomaly monitoring.
- Optional demand forecasting page.

## Planned Impact Metrics

- Number of countries tracked.
- Number of hourly records processed.
- Pipeline runtime.
- Data freshness.
- Data quality pass rate.
- Number of dashboard pages.
- Forecasting accuracy if the ML extension is implemented.

## How to Run Locally

Create a `.env` file:

```bash
cp .env.example .env
```

Run a small Open-Meteo API smoke test:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pandas requests
python -m scripts.run_weather_sample --start-date 2024-01-01 --end-date 2024-01-03 --countries IT FR
```

The sample output is written to `data/processed/`.

Docker is required for the PostgreSQL and dashboard workflow. Install Docker Desktop first if `docker --version` does not work.

Start PostgreSQL and the dashboard:

```bash
docker compose up --build
```

Run the Prefect flow manually:

```bash
python -m src.pipeline.prefect_flow
```

## Resume-Ready Summary

Built an end-to-end European energy and weather analytics pipeline using Python, PostgreSQL, Docker, Prefect, SQL, and Streamlit to ingest, validate, store, analyze, and visualize public API data.
