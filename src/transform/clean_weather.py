import pandas as pd


def clean_weather(df):
    df = df.copy()
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True)

    numeric_columns = [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "cloud_cover",
        "wind_speed_10m",
        "wind_speed_100m",
        "shortwave_radiation",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    return df.drop_duplicates(subset=["country_code", "timestamp_utc"])

