# Architecture

Author: Mohammad Mohammadi

## Goal

This project is designed as a complete data pipeline, not only as an analysis notebook. The pipeline collects weather and electricity data, stores it in PostgreSQL, validates it, transforms it into analytics-ready tables, and exposes insights through a dashboard.

## Data Flow

```text
Public APIs
  - Open-Meteo Historical Weather API
  - ENTSO-E Transparency Platform
  - Optional Eurostat and Terna data

        |
        v

Python extraction layer
  - API requests
  - response parsing
  - raw snapshots

        |
        v

Transformation layer
  - timestamp normalization
  - country-code standardization
  - missing value handling
  - duplicate removal
  - hourly grain alignment

        |
        v

PostgreSQL
  - dimension tables
  - hourly fact tables
  - daily analytics marts

        |
        v

Quality checks
  - null checks
  - duplicate checks
  - range checks
  - freshness checks

        |
        v

Prefect orchestration
  - historical backfills
  - daily incremental runs
  - task logs

        |
        v

Streamlit dashboard
  - overview
  - trends
  - country comparison
  - anomalies
  - optional forecasting
```

## Design Choices

- I use PostgreSQL to demonstrate relational data modeling and SQL analytics.
- I use Prefect because it is lighter than Airflow for a student portfolio project but still demonstrates orchestration.
- I use Docker Compose to make the project reproducible.
- I keep raw and analytics layers separate so the project resembles a real data engineering workflow.

