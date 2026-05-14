import pandas as pd


def clean_load(df):
    df = df.copy()
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True)
    df["load_mw"] = pd.to_numeric(df["load_mw"], errors="coerce")
    return df.drop_duplicates(subset=["country_code", "timestamp_utc"])


def clean_prices(df):
    df = df.copy()
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True)
    df["price_eur_mwh"] = pd.to_numeric(df["price_eur_mwh"], errors="coerce")
    return df.drop_duplicates(subset=["country_code", "timestamp_utc"])

