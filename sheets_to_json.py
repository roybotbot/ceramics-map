#!/usr/bin/env python3
"""
sheets_to_json.py — Sync Google Sheets → studios.json

Fetches studio data from a public Google Sheet, geocodes any new addresses
using the existing studios.json as a cache, and writes the result.

Usage:
    SHEET_URL="https://..." python3 sheets_to_json.py

Set SHEET_URL as a GitHub Actions variable, or export it in your shell locally.
"""

import csv
import io
import json
import os
import re
import time
import requests

SHEET_URL   = os.environ.get("SHEET_URL", "")
STUDIOS_JSON = os.path.join(os.path.dirname(__file__), "studios.json")
USER_AGENT  = "ma-pottery-map/1.0 hi@roysclay.co"


def fetch_sheet(url: str) -> list[dict]:
    """Download the public Google Sheet as CSV and return rows as dicts."""
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    reader = csv.DictReader(io.StringIO(resp.text))
    return list(reader)


def load_geocache() -> dict[str, list[float]]:
    """Read existing studios.json and return address → [lon, lat] lookup."""
    try:
        with open(STUDIOS_JSON) as f:
            data = json.load(f)
        return {
            feat["properties"]["address"]: feat["geometry"]["coordinates"]
            for feat in data.get("features", [])
        }
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def clean_address(address: str) -> str:
    """Strip unit/suite/floor info and building name prefixes that confuse Nominatim.
    The original address is preserved in the data — this is only used for geocoding."""

    # Drop building name / entrance note prefix if the first comma-segment has no street number
    # e.g. "O'donnel Building, 365 Moody St, Waltham, MA" → "365 Moody St, Waltham, MA"
    parts = [p.strip() for p in address.split(',')]
    if parts and not re.search(r'\d', parts[0]):
        parts = parts[1:]
    address = ', '.join(parts)

    # Remove unit/suite/floor/apt designations and everything that follows on the same segment
    # e.g. "1060 Broadway Unit C001" → "1060 Broadway"
    address = re.sub(
        r'\s+(#|Unit|Ste\.?|Suite|STE|Apt\.?|Rm\.?|Room|Floor|Fl\.?|Studio|Bldg\.?|Building)'
        r'[\s\w&\-/]*',
        '', address, flags=re.IGNORECASE
    )

    # Remove ordinal floor descriptions: "3rd Floor", "2nd floor"
    address = re.sub(r'\s+\d+(st|nd|rd|th)\s+[Ff]loor', '', address)

    return address.strip()


def geocode(address: str) -> list[float] | None:
    """Return [lon, lat] for an address using Nominatim, or None on failure."""
    query   = clean_address(address)
    params  = {"q": query, "format": "json", "limit": 1, "countrycodes": "us"}
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params=params, headers=headers, timeout=10
        )
        resp.raise_for_status()
        results = resp.json()
        if results:
            return [float(results[0]["lon"]), float(results[0]["lat"])]
        print(f"  ⚠  No geocoding result for: {address} (tried: {query})")
        return None
    except Exception as e:
        print(f"  ⚠  Error geocoding '{address}': {e}")
        return None


def parse_bool(val: str) -> bool:
    return val.strip().upper() in ("TRUE", "YES", "1", "X")


def main():
    if not SHEET_URL:
        raise SystemExit("Error: SHEET_URL environment variable is not set.")

    print("Fetching sheet…")
    rows = fetch_sheet(SHEET_URL)
    print(f"  {len(rows)} rows found in sheet")

    geocache = load_geocache()
    print(f"  {len(geocache)} addresses already geocoded (cached)")

    features = []
    for row in rows:
        name    = row.get("name", "").strip()
        address = row.get("address", "").strip()

        if not name or not address:
            continue  # skip empty rows

        if address in geocache:
            coords = geocache[address]
            print(f"  ✓ (cached)  {name}")
        else:
            print(f"  ⟳ Geocoding {name} — {address}")
            coords = geocode(address)
            if coords is None:
                print(f"  ✗ Skipping  {name}")
                continue
            geocache[address] = coords
            time.sleep(1)  # Nominatim rate limit: 1 req/sec

        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": coords},
            "properties": {
                "name":          name,
                "address":       address,
                "website":       row.get("website",       "").strip(),
                "phone":         row.get("phone",         "").strip(),
                "classes":        parse_bool(row.get("classes",        "")),
                "open_studio":    parse_bool(row.get("open_studio",    "")),
                "member_studios": parse_bool(row.get("member_studios", "")),
                "gallery":        parse_bool(row.get("gallery",        "")),
                "supplies":       parse_bool(row.get("supplies",       "")),
                "artist_studio":  parse_bool(row.get("artist_studio",  "")),
                "notes":          row.get("notes", "").strip(),
            }
        })

    geojson = {"type": "FeatureCollection", "features": features}
    with open(STUDIOS_JSON, "w") as f:
        json.dump(geojson, f, indent=2)

    print(f"\nDone — {len(features)} studios written to studios.json")


if __name__ == "__main__":
    main()
