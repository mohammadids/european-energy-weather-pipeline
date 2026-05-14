import pandas as pd

from src.transform.clean_weather import clean_weather


def test_clean_weather_removes_duplicate_country_timestamps():
    df = pd.DataFrame(
        {
            "country_code": ["IT", "IT"],
            "city": ["Rome", "Rome"],
            "timestamp_utc": ["2024-01-01T00:00:00Z", "2024-01-01T00:00:00Z"],
            "temperature_2m": ["10.5", "10.5"],
            "relative_humidity_2m": [70, 70],
            "precipitation": [0, 0],
            "cloud_cover": [20, 20],
            "wind_speed_10m": [5, 5],
            "wind_speed_100m": [10, 10],
            "shortwave_radiation": [0, 0],
        }
    )

    cleaned = clean_weather(df)

    assert len(cleaned) == 1
    assert cleaned["temperature_2m"].dtype.kind in "fi"

