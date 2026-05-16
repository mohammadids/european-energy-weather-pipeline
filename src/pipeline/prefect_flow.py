import os

from prefect import flow, task

from src.config import COUNTRIES, DATABASE_URL
from src.extract.energy_api import extract_day_ahead_prices, extract_load
from src.extract.weather_api import extract_weather
from src.load.postgres_loader import load_dataframe, refresh_daily_mart
from src.transform.clean_energy import clean_load, clean_prices
from src.transform.clean_weather import clean_weather
from src.validation.quality_checks import validate_load, validate_prices, validate_weather


@task
def process_weather(country_config, start_date, end_date):
    weather = extract_weather(
        country_config.country_code,
        country_config.city,
        country_config.latitude,
        country_config.longitude,
        start_date,
        end_date,
    )
    weather = clean_weather(weather)
    validate_weather(weather)
    load_dataframe(weather, "fact_weather_hourly", DATABASE_URL)


@task
def process_energy(country_code, start_date, end_date):
    load = extract_load(country_code, start_date, end_date)
    load = clean_load(load)
    validate_load(load)
    load_dataframe(load, "fact_energy_load_hourly", DATABASE_URL)

    prices = extract_day_ahead_prices(country_code, start_date, end_date)
    prices = clean_prices(prices)
    validate_prices(prices)
    load_dataframe(prices, "fact_energy_price_hourly", DATABASE_URL)


@task
def refresh_analytics():
    refresh_daily_mart(DATABASE_URL)


@flow(name="european-energy-weather-pipeline")
def energy_weather_pipeline(start_date="2024-01-01", end_date="2024-01-07", include_energy=False):
    for country_config in COUNTRIES.values():
        process_weather(country_config, start_date, end_date)

        if include_energy:
            process_energy(country_config.country_code, start_date, end_date)

    refresh_analytics()


def env_flag(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "y"}


if __name__ == "__main__":
    energy_weather_pipeline(
        start_date=os.getenv("START_DATE", "2024-01-01"),
        end_date=os.getenv("END_DATE", "2024-01-07"),
        include_energy=env_flag("INCLUDE_ENERGY", False),
    )
