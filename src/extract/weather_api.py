import pandas as pd
import requests

OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


def extract_weather(country_code, city, latitude, longitude, start_date, end_date):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
                "cloud_cover",
                "wind_speed_10m",
                "wind_speed_100m",
                "shortwave_radiation",
            ]
        ),
        "timezone": "UTC",
    }

    response = requests.get(OPEN_METEO_ARCHIVE_URL, params=params, timeout=30)
    response.raise_for_status()

    hourly = response.json()["hourly"]
    df = pd.DataFrame(hourly)
    df["country_code"] = country_code
    df["city"] = city
    df["timestamp_utc"] = pd.to_datetime(df["time"], utc=True)
    return df.drop(columns=["time"])

