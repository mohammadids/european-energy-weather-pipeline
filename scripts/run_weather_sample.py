import argparse
from pathlib import Path

import pandas as pd

from src.config import COUNTRIES
from src.extract.weather_api import extract_weather
from src.transform.clean_weather import clean_weather
from src.validation.quality_checks import validate_weather


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract a small Open-Meteo weather sample and save it locally."
    )
    parser.add_argument("--start-date", default="2024-01-01")
    parser.add_argument("--end-date", default="2024-01-03")
    parser.add_argument("--countries", nargs="+", default=["IT", "FR"])
    return parser.parse_args()


def main():
    args = parse_args()
    frames = []

    for country_code in args.countries:
        country = COUNTRIES[country_code]
        weather = extract_weather(
            country.country_code,
            country.city,
            country.latitude,
            country.longitude,
            args.start_date,
            args.end_date,
        )
        weather = clean_weather(weather)
        validate_weather(weather)
        frames.append(weather)

    result = pd.concat(frames, ignore_index=True)
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"weather_sample_{args.start_date}_{args.end_date}.csv"
    result.to_csv(output_path, index=False)

    print(f"Saved {len(result):,} weather rows to {output_path}")
    print(f"Countries: {', '.join(args.countries)}")
    print(f"Timestamp range: {result['timestamp_utc'].min()} to {result['timestamp_utc'].max()}")


if __name__ == "__main__":
    main()
