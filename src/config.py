import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()


@dataclass(frozen=True)
class CountryConfig:
    country_code: str
    city: str
    latitude: float
    longitude: float


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://mohammad:mohammad_password@localhost:5432/energy_weather",
)

COUNTRIES = {
    "IT": CountryConfig("IT", "Rome", 41.9028, 12.4964),
    "FR": CountryConfig("FR", "Paris", 48.8566, 2.3522),
    "ES": CountryConfig("ES", "Madrid", 40.4168, -3.7038),
    "DE_LU": CountryConfig("DE_LU", "Berlin", 52.5200, 13.4050),
}
