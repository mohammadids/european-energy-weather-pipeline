import pandas as pd

from src.transform.clean_energy import clean_load, clean_prices
from src.transform.clean_weather import clean_weather


def test_clean_weather_casts_numeric_columns_and_removes_duplicates():
    df = pd.DataFrame(
        {
            "country_code": ["IT", "IT"],
            "city": ["Rome", "Rome"],
            "timestamp_utc": ["2024-01-01T00:00:00Z", "2024-01-01T00:00:00Z"],
            "temperature_2m": ["10.5", "10.5"],
            "relative_humidity_2m": ["70", "70"],
            "precipitation": ["0", "0"],
            "cloud_cover": ["20", "20"],
            "wind_speed_10m": ["5", "5"],
            "wind_speed_100m": ["10", "10"],
            "shortwave_radiation": ["0", "0"],
        }
    )

    cleaned = clean_weather(df)

    assert len(cleaned) == 1
    assert cleaned["timestamp_utc"].dt.tz is not None
    assert cleaned["temperature_2m"].dtype.kind in "fi"
    assert cleaned["relative_humidity_2m"].dtype.kind in "fi"


def test_clean_load_resamples_subhourly_values_to_hourly_average():
    df = pd.DataFrame(
        {
            "country_code": ["ES", "ES", "ES", "ES"],
            "timestamp_utc": [
                "2024-01-01T00:00:00Z",
                "2024-01-01T00:15:00Z",
                "2024-01-01T00:30:00Z",
                "2024-01-01T00:45:00Z",
            ],
            "load_mw": ["100", "120", "140", "160"],
        }
    )

    cleaned = clean_load(df)

    assert len(cleaned) == 1
    assert cleaned.loc[0, "country_code"] == "ES"
    assert cleaned.loc[0, "timestamp_utc"] == pd.Timestamp("2024-01-01T00:00:00Z")
    assert cleaned.loc[0, "load_mw"] == 130


def test_clean_load_keeps_country_resampling_separate():
    df = pd.DataFrame(
        {
            "country_code": ["ES", "ES", "FR", "FR"],
            "timestamp_utc": [
                "2024-01-01T00:00:00Z",
                "2024-01-01T00:30:00Z",
                "2024-01-01T00:00:00Z",
                "2024-01-01T00:30:00Z",
            ],
            "load_mw": [100, 200, 300, 500],
        }
    )

    cleaned = clean_load(df).sort_values("country_code").reset_index(drop=True)

    assert len(cleaned) == 2
    assert cleaned.loc[0, "country_code"] == "ES"
    assert cleaned.loc[0, "load_mw"] == 150
    assert cleaned.loc[1, "country_code"] == "FR"
    assert cleaned.loc[1, "load_mw"] == 400


def test_clean_prices_casts_numeric_values_and_removes_duplicates():
    df = pd.DataFrame(
        {
            "country_code": ["FR", "FR"],
            "timestamp_utc": ["2024-01-01T00:00:00Z", "2024-01-01T00:00:00Z"],
            "price_eur_mwh": ["64.25", "64.25"],
        }
    )

    cleaned = clean_prices(df)

    assert len(cleaned) == 1
    assert cleaned["timestamp_utc"].dt.tz is not None
    assert cleaned["price_eur_mwh"].dtype.kind in "fi"
