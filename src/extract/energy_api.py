import os

import pandas as pd

ENTSOE_PRICE_AREA_CODES = {
    "IT": "IT_NORD",
}


def get_entsoe_client():
    from entsoe import EntsoePandasClient

    api_key = os.getenv("ENTSOE_API_KEY")
    if not api_key or api_key == "replace_with_your_entsoe_token":
        raise ValueError("ENTSOE_API_KEY is required for ENTSO-E extraction")

    return EntsoePandasClient(api_key=api_key)


def build_entsoe_window(start_date, end_date):
    start = pd.Timestamp(start_date, tz="UTC")
    end = pd.Timestamp(end_date, tz="UTC") + pd.Timedelta(days=1)
    return start, end


def normalize_entsoe_timeseries(data, country_code, value_column, preferred_columns=None):
    preferred_columns = preferred_columns or []

    if isinstance(data, pd.Series):
        df = data.rename(value_column).reset_index()
    else:
        df = data.reset_index()
        if value_column not in df.columns:
            for column in preferred_columns:
                if column in df.columns:
                    df = df.rename(columns={column: value_column})
                    break

    timestamp_column = df.columns[0]
    df = df.rename(columns={timestamp_column: "timestamp_utc"})

    if value_column not in df.columns:
        numeric_columns = [
            column
            for column in df.columns
            if column != "timestamp_utc" and pd.api.types.is_numeric_dtype(df[column])
        ]
        if not numeric_columns:
            raise ValueError(f"Could not find ENTSO-E value column for {value_column}")
        df = df.rename(columns={numeric_columns[0]: value_column})

    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True)
    df[value_column] = pd.to_numeric(df[value_column], errors="coerce")
    df["country_code"] = country_code
    return df[["country_code", "timestamp_utc", value_column]].dropna(subset=[value_column])


def filter_entsoe_window(df, start, end):
    return df[(df["timestamp_utc"] >= start) & (df["timestamp_utc"] < end)]


def extract_load(country_code, start_date, end_date):
    client = get_entsoe_client()
    start, end = build_entsoe_window(start_date, end_date)
    data = client.query_load(country_code, start=start, end=end)
    df = normalize_entsoe_timeseries(
        data,
        country_code,
        "load_mw",
        preferred_columns=["Actual Load", "Load"],
    )
    return filter_entsoe_window(df, start, end)


def extract_day_ahead_prices(country_code, start_date, end_date):
    client = get_entsoe_client()
    start, end = build_entsoe_window(start_date, end_date)
    price_area_code = ENTSOE_PRICE_AREA_CODES.get(country_code, country_code)
    data = client.query_day_ahead_prices(price_area_code, start=start, end=end)
    df = normalize_entsoe_timeseries(data, country_code, "price_eur_mwh")
    return filter_entsoe_window(df, start, end)
