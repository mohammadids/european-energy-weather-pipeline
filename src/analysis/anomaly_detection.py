import pandas as pd


def _z_score_by_country(df: pd.DataFrame, value_column: str) -> pd.Series:
    grouped = df.groupby("country_code")[value_column]
    mean = grouped.transform("mean")
    std = grouped.transform(lambda series: series.std(ddof=0))
    return ((df[value_column] - mean) / std.replace(0, pd.NA)).fillna(0.0)


def detect_daily_anomalies(
    daily_df: pd.DataFrame,
    threshold: float = 2.0,
) -> pd.DataFrame:
    """Flag unusual daily price and load values inside each country.

    The method is intentionally simple and explainable for a portfolio project:
    each country's daily values are compared with that country's own average
    and standard deviation. This keeps Italy's prices, France's load, and other
    markets from being compared on the wrong scale.
    """
    required_columns = {
        "country_code",
        "date",
        "avg_price_eur_mwh",
        "avg_load_mw",
    }
    missing_columns = required_columns.difference(daily_df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns for anomaly detection: {missing}")

    anomalies = daily_df.copy()
    anomalies["price_z_score"] = _z_score_by_country(anomalies, "avg_price_eur_mwh")
    anomalies["load_z_score"] = _z_score_by_country(anomalies, "avg_load_mw")
    anomalies["is_price_anomaly"] = anomalies["price_z_score"].abs() >= threshold
    anomalies["is_load_anomaly"] = anomalies["load_z_score"].abs() >= threshold
    anomalies["is_anomaly"] = anomalies["is_price_anomaly"] | anomalies["is_load_anomaly"]
    anomalies["max_abs_z_score"] = anomalies[["price_z_score", "load_z_score"]].abs().max(axis=1)

    conditions = [
        anomalies["price_z_score"] >= threshold,
        anomalies["price_z_score"] <= -threshold,
        anomalies["load_z_score"] >= threshold,
        anomalies["load_z_score"] <= -threshold,
    ]
    labels = [
        "High price",
        "Low price",
        "High load",
        "Low load",
    ]
    anomalies["anomaly_type"] = "Normal"
    for condition, label in zip(conditions, labels):
        anomalies.loc[condition & (anomalies["anomaly_type"] == "Normal"), "anomaly_type"] = label

    return anomalies.sort_values(["date", "country_code"]).reset_index(drop=True)
