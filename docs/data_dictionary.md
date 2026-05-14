# Data Dictionary

Author: Mohammad Mohammadi

## dim_country

| Column | Description |
|---|---|
| country_code | Country or bidding-zone code, such as IT, FR, ES, DE_LU |
| country_name | Human-readable country or bidding-zone name |
| bidding_zone | ENTSO-E bidding-zone label |

## dim_city

| Column | Description |
|---|---|
| city_id | Surrogate city identifier |
| country_code | Country code linked to `dim_country` |
| city_name | Representative city used for weather extraction |
| latitude | City latitude |
| longitude | City longitude |

## fact_weather_hourly

| Column | Description |
|---|---|
| country_code | Country or bidding-zone code |
| city | Representative weather city |
| timestamp_utc | Hourly UTC timestamp |
| temperature_2m | Air temperature at 2 meters, Celsius |
| relative_humidity_2m | Relative humidity percentage |
| precipitation | Hourly precipitation, millimeters |
| cloud_cover | Cloud cover percentage |
| wind_speed_10m | Wind speed at 10 meters |
| wind_speed_100m | Wind speed at 100 meters |
| shortwave_radiation | Solar shortwave radiation |

## fact_energy_load_hourly

| Column | Description |
|---|---|
| country_code | Country or bidding-zone code |
| timestamp_utc | Hourly UTC timestamp |
| load_mw | Actual electricity load in megawatts |

## fact_energy_price_hourly

| Column | Description |
|---|---|
| country_code | Country or bidding-zone code |
| timestamp_utc | Hourly UTC timestamp |
| price_eur_mwh | Day-ahead electricity price in EUR/MWh |

## fact_generation_hourly

| Column | Description |
|---|---|
| country_code | Country or bidding-zone code |
| timestamp_utc | Hourly UTC timestamp |
| energy_source | Generation source, such as solar, wind, fossil gas, hydro |
| generation_mw | Electricity generation in megawatts |

