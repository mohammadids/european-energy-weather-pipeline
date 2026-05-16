import pandas as pd
import pytest

from src.analysis.anomaly_detection import detect_daily_anomalies


def sample_daily_frame():
    return pd.DataFrame(
        {
            "country_code": ["IT"] * 5 + ["FR"] * 5,
            "date": pd.date_range("2024-01-01", periods=5).tolist() * 2,
            "avg_price_eur_mwh": [80, 82, 81, 79, 160, 55, 56, 54, 55, 55],
            "avg_load_mw": [30000, 30500, 30200, 29900, 30100, 50000, 50500, 49800, 50200, 70000],
        }
    )


def test_detect_daily_anomalies_flags_price_and_load_outliers_by_country():
    anomalies = detect_daily_anomalies(sample_daily_frame(), threshold=1.5)

    italy_outlier = anomalies[
        (anomalies["country_code"] == "IT")
        & (anomalies["date"] == pd.Timestamp("2024-01-05"))
    ].iloc[0]
    france_outlier = anomalies[
        (anomalies["country_code"] == "FR")
        & (anomalies["date"] == pd.Timestamp("2024-01-05"))
    ].iloc[0]

    assert italy_outlier["is_price_anomaly"]
    assert italy_outlier["anomaly_type"] == "High price"
    assert france_outlier["is_load_anomaly"]
    assert france_outlier["anomaly_type"] == "High load"


def test_detect_daily_anomalies_handles_constant_country_values():
    df = pd.DataFrame(
        {
            "country_code": ["ES", "ES"],
            "date": pd.date_range("2024-01-01", periods=2),
            "avg_price_eur_mwh": [40, 40],
            "avg_load_mw": [25000, 25000],
        }
    )

    anomalies = detect_daily_anomalies(df)

    assert not anomalies["is_anomaly"].any()
    assert anomalies["price_z_score"].eq(0).all()
    assert anomalies["load_z_score"].eq(0).all()


def test_detect_daily_anomalies_requires_expected_columns():
    with pytest.raises(ValueError, match="Missing required columns"):
        detect_daily_anomalies(pd.DataFrame({"country_code": ["IT"]}))
