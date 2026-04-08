"""Fetch weather data for a circuit session via OpenWeatherMap."""
from __future__ import annotations

import argparse
import os
import requests


def fetch_weather(lat: float, lon: float, api_key: str) -> dict:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lat", type=float, default=26.0325)
    parser.add_argument("--lon", type=float, default=50.5106)
    args = parser.parse_args()

    key = os.getenv("OPENWEATHER_API_KEY")
    if not key:
        raise SystemExit("Missing OPENWEATHER_API_KEY")

    data = fetch_weather(args.lat, args.lon, key)
    print("temp_c", data.get("main", {}).get("temp"))


if __name__ == "__main__":
    main()
