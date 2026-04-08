"""Jolpica API client for historical results and pit stops."""
from __future__ import annotations

import argparse
import requests

BASE_URL = "https://api.jolpi.ca/ergast/f1"


def fetch_race_results(season: int, round_no: int) -> dict:
    url = f"{BASE_URL}/{season}/{round_no}/results.json"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", type=int, default=2023)
    parser.add_argument("--round", type=int, default=1)
    args = parser.parse_args()

    data = fetch_race_results(args.season, args.round)
    races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    if not races:
        print("No data returned")
        return
    print("Race:", races[0].get("raceName"))
    print("Results:")
    for r in races[0].get("Results", [])[:5]:
        print(r["position"], r["Driver"]["familyName"], r["Constructor"]["name"])


if __name__ == "__main__":
    main()
