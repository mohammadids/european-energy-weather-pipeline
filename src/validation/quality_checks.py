def validate_weather(df):
    assert df["timestamp_utc"].notna().all(), "Weather timestamps contain nulls"
    assert df["country_code"].notna().all(), "Weather country codes contain nulls"
    assert df["temperature_2m"].between(-40, 60).all(), "Temperature outside expected range"
    assert df["wind_speed_10m"].ge(0).all(), "Wind speed cannot be negative"
    assert not df.duplicated(["country_code", "timestamp_utc"]).any(), "Duplicate weather rows found"


def validate_load(df):
    assert df["timestamp_utc"].notna().all(), "Load timestamps contain nulls"
    assert df["country_code"].notna().all(), "Load country codes contain nulls"
    assert df["load_mw"].gt(0).all(), "Electricity load must be positive"
    assert not df.duplicated(["country_code", "timestamp_utc"]).any(), "Duplicate load rows found"


def validate_prices(df):
    assert df["timestamp_utc"].notna().all(), "Price timestamps contain nulls"
    assert df["country_code"].notna().all(), "Price country codes contain nulls"
    assert df["price_eur_mwh"].notna().all(), "Electricity price contains nulls"
    assert not df.duplicated(["country_code", "timestamp_utc"]).any(), "Duplicate price rows found"

