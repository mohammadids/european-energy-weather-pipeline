CREATE TABLE IF NOT EXISTS dim_country (
    country_code VARCHAR(10) PRIMARY KEY,
    country_name TEXT NOT NULL,
    bidding_zone TEXT
);

CREATE TABLE IF NOT EXISTS dim_city (
    city_id SERIAL PRIMARY KEY,
    country_code VARCHAR(10) REFERENCES dim_country(country_code),
    city_name TEXT NOT NULL,
    latitude NUMERIC(9,6),
    longitude NUMERIC(9,6)
);

CREATE TABLE IF NOT EXISTS fact_weather_hourly (
    country_code VARCHAR(10) REFERENCES dim_country(country_code),
    city TEXT,
    timestamp_utc TIMESTAMPTZ NOT NULL,
    temperature_2m NUMERIC,
    relative_humidity_2m NUMERIC,
    precipitation NUMERIC,
    cloud_cover NUMERIC,
    wind_speed_10m NUMERIC,
    wind_speed_100m NUMERIC,
    shortwave_radiation NUMERIC,
    inserted_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (country_code, timestamp_utc)
);

CREATE TABLE IF NOT EXISTS fact_energy_load_hourly (
    country_code VARCHAR(10) REFERENCES dim_country(country_code),
    timestamp_utc TIMESTAMPTZ NOT NULL,
    load_mw NUMERIC NOT NULL,
    inserted_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (country_code, timestamp_utc)
);

CREATE TABLE IF NOT EXISTS fact_energy_price_hourly (
    country_code VARCHAR(10) REFERENCES dim_country(country_code),
    timestamp_utc TIMESTAMPTZ NOT NULL,
    price_eur_mwh NUMERIC,
    currency TEXT DEFAULT 'EUR',
    price_unit TEXT DEFAULT 'MWh',
    inserted_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (country_code, timestamp_utc)
);

CREATE TABLE IF NOT EXISTS fact_generation_hourly (
    country_code VARCHAR(10) REFERENCES dim_country(country_code),
    timestamp_utc TIMESTAMPTZ NOT NULL,
    energy_source TEXT NOT NULL,
    generation_mw NUMERIC,
    inserted_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (country_code, timestamp_utc, energy_source)
);

INSERT INTO dim_country (country_code, country_name, bidding_zone)
VALUES
    ('IT', 'Italy', 'Italy'),
    ('FR', 'France', 'France'),
    ('ES', 'Spain', 'Spain'),
    ('DE_LU', 'Germany/Luxembourg', 'Germany/Luxembourg')
ON CONFLICT (country_code) DO NOTHING;

INSERT INTO dim_city (country_code, city_name, latitude, longitude)
VALUES
    ('IT', 'Rome', 41.9028, 12.4964),
    ('FR', 'Paris', 48.8566, 2.3522),
    ('ES', 'Madrid', 40.4168, -3.7038),
    ('DE_LU', 'Berlin', 52.5200, 13.4050);

CREATE MATERIALIZED VIEW IF NOT EXISTS mart_daily_country_energy_weather AS
SELECT
    w.country_code,
    DATE(w.timestamp_utc) AS date,
    AVG(w.temperature_2m) AS avg_temperature_2m,
    AVG(w.wind_speed_100m) AS avg_wind_speed_100m,
    AVG(w.shortwave_radiation) AS avg_shortwave_radiation,
    AVG(l.load_mw) AS avg_load_mw,
    MAX(l.load_mw) AS peak_load_mw,
    AVG(p.price_eur_mwh) AS avg_price_eur_mwh
FROM fact_weather_hourly w
LEFT JOIN fact_energy_load_hourly l
    ON w.country_code = l.country_code
   AND w.timestamp_utc = l.timestamp_utc
LEFT JOIN fact_energy_price_hourly p
    ON w.country_code = p.country_code
   AND w.timestamp_utc = p.timestamp_utc
GROUP BY w.country_code, DATE(w.timestamp_utc);

