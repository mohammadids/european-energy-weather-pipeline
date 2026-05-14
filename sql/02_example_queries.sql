-- Weather and demand by day
SELECT
    w.country_code,
    DATE(w.timestamp_utc) AS date,
    AVG(w.temperature_2m) AS avg_temperature,
    AVG(l.load_mw) AS avg_load_mw
FROM fact_weather_hourly w
JOIN fact_energy_load_hourly l
    ON w.country_code = l.country_code
   AND w.timestamp_utc = l.timestamp_utc
GROUP BY w.country_code, DATE(w.timestamp_utc)
ORDER BY date, country_code;

-- Negative electricity price hours
SELECT
    country_code,
    COUNT(*) AS negative_price_hours,
    MIN(price_eur_mwh) AS lowest_price_eur_mwh
FROM fact_energy_price_hourly
WHERE price_eur_mwh < 0
GROUP BY country_code
ORDER BY negative_price_hours DESC;

-- Most recent timestamp by table
SELECT 'weather' AS table_name, MAX(timestamp_utc) AS latest_timestamp
FROM fact_weather_hourly
UNION ALL
SELECT 'load' AS table_name, MAX(timestamp_utc) AS latest_timestamp
FROM fact_energy_load_hourly
UNION ALL
SELECT 'prices' AS table_name, MAX(timestamp_utc) AS latest_timestamp
FROM fact_energy_price_hourly;

