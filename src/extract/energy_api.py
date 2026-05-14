import os


def get_entsoe_client():
    from entsoe import Client

    api_key = os.getenv("ENTSOE_API_KEY")
    if not api_key or api_key == "replace_with_your_entsoe_token":
        raise ValueError("ENTSOE_API_KEY is required for ENTSO-E extraction")

    return Client(api_key=os.getenv("ENTSOE_API_KEY"))


def extract_load(country_code, start_date, end_date):
    client = get_entsoe_client()
    df = client.load.actual(start_date, end_date, country=country_code)
    df["country_code"] = country_code
    return df.rename(columns={"timestamp": "timestamp_utc", "value": "load_mw"})


def extract_day_ahead_prices(country_code, start_date, end_date):
    client = get_entsoe_client()
    df = client.prices.day_ahead(start_date, end_date, country=country_code)
    df["country_code"] = country_code
    return df.rename(columns={"timestamp": "timestamp_utc", "value": "price_eur_mwh"})
