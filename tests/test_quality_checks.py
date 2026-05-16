import pandas as pd
import pytest

from src.validation.quality_checks import validate_load, validate_prices, validate_weather


def valid_weather_frame():
    return pd.DataFrame(
        {
            "country_code": ["IT"],
            "timestamp_utc": [pd.Timestamp("2024-01-01T00:00:00Z")],
            "temperature_2m": [12.5],
            "wind_speed_10m": [4.0],
        }
    )


def valid_load_frame():
    return pd.DataFrame(
        {
            "country_code": ["FR"],
            "timestamp_utc": [pd.Timestamp("2024-01-01T00:00:00Z")],
            "load_mw": [52000.0],
        }
    )


def valid_price_frame():
    return pd.DataFrame(
        {
            "country_code": ["DE_LU"],
            "timestamp_utc": [pd.Timestamp("2024-01-01T00:00:00Z")],
            "price_eur_mwh": [75.5],
        }
    )


def test_validate_weather_accepts_valid_weather_data():
    validate_weather(valid_weather_frame())


def test_validate_weather_rejects_temperature_outside_expected_range():
    df = valid_weather_frame()
    df.loc[0, "temperature_2m"] = 90

    with pytest.raises(AssertionError, match="Temperature outside expected range"):
        validate_weather(df)


def test_validate_weather_rejects_duplicate_country_timestamp():
    df = pd.concat([valid_weather_frame(), valid_weather_frame()], ignore_index=True)

    with pytest.raises(AssertionError, match="Duplicate weather rows found"):
        validate_weather(df)


def test_validate_load_accepts_valid_load_data():
    validate_load(valid_load_frame())


def test_validate_load_rejects_non_positive_load():
    df = valid_load_frame()
    df.loc[0, "load_mw"] = 0

    with pytest.raises(AssertionError, match="Electricity load must be positive"):
        validate_load(df)


def test_validate_prices_accepts_valid_price_data():
    validate_prices(valid_price_frame())


def test_validate_prices_rejects_null_price():
    df = valid_price_frame()
    df.loc[0, "price_eur_mwh"] = None

    with pytest.raises(AssertionError, match="Electricity price contains nulls"):
        validate_prices(df)
