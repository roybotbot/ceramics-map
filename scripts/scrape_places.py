#!/usr/bin/env python3
"""
scrape_places.py — Search Google Places API (New) for ceramics/pottery studios
Uses geographic bounding boxes per region so no locations get missed.
Outputs studios_raw.csv ready to review and paste into your Google Sheet.

Usage:
    PLACES_API_KEY="your_key_here" SHEET_URL="https://..." python3 scrape_places.py

SHEET_URL is optional — if provided, any studio already in your Google Sheet
will be skipped so you only get genuinely new results.
"""

import csv
import io
import os
import re
import time
import requests

API_KEY   = os.environ.get("PLACES_API_KEY", "")
SHEET_URL = os.environ.get("SHEET_URL", "")

# ── Search terms (no location — that's handled by the bounding box) ──────────
TERMS = [
    "pottery studio",
    "ceramics studio",
    "pottery classes",
    "ceramics classes",
    "pottery supply",
    "ceramic supply",
]

# ── Geographic regions with bounding boxes ────────────────────────────────────
# Each region is searched with every term above. Results are deduplicated by place ID.
REGIONS = [
    {
        "name": "Massachusetts",
        "bounds": {
            "low":  {"latitude": 41.19, "longitude": -73.51},
            "high": {"latitude": 42.89, "longitude": -69.93},
        },
    },
    {
        "name": "Rhode Island",
        "bounds": {
            "low":  {"latitude": 41.15, "longitude": -71.89},
            "high": {"latitude": 42.02, "longitude": -71.12},
        },
    },
    {
        "name": "Southern New Hampshire",
        "bounds": {
            "low":  {"latitude": 42.70, "longitude": -72.55},
            "high": {"latitude": 43.40, "longitude": -70.70},
        },
    },
    {
        "name": "Southern Vermont",
        "bounds": {
            "low":  {"latitude": 42.72, "longitude": -73.44},
            "high": {"latitude": 43.30, "longitude": -72.45},
        },
    },
    {
        "name": "Northern Connecticut",
        "bounds": {
            "low":  {"latitude": 41.20, "longitude": -73.00},
            "high": {"latitude": 42.05, "longitude": -71.80},
        },
    },
    {
        "name": "Hudson Valley / Eastern New York",
        "bounds": {
            "low":  {"latitude": 41.50, "longitude": -74.30},
            "high": {"latitude": 43.30, "longitude": -73.50},
        },
    },
    {
        "name": "Southern Maine",
        "bounds": {
            "low":  {"latitude": 43.00, "longitude": -71.30},
            "high": {"latitude": 44.50, "longitude": -69.90},
        },
    },
]

REPO_ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(REPO_ROOT, "studios_raw.csv")
SEARCH_URL  = "https://places.googleapis.com/v1/places:searchText"
FIELD_MASK  = "places.id,places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.websiteUri"


def normalize(text: str) -> str:
    """Lowercase, remove zip codes and punctuation for loose matching."""
    text = text.lower()
    text = re.sub(r'\b\d{5}(-\d{4})?\b', '', text)  # strip zip codes
    text = re.sub(r'[^\w\s]', '', text)               # strip punctuation
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def load_existing_sheet() -> tuple[set, set]:
    """Fetch the Google Sheet and return sets of normalized names and addresses."""
    if not SHEET_URL:
        return set(), set()
    try:
        resp = requests.get(SHEET_URL, timeout=15)
        resp.raise_for_status()
        reader = csv.DictReader(io.StringIO(resp.text))
        names     = set()
        addresses = set()
        for row in reader:
            if row.get("name"):
                names.add(normalize(row["name"]))
            if row.get("address"):
                addresses.add(normalize(row["address"]))
        print(f"  {len(names)} existing entries loaded from sheet")
        return names, addresses
    except Exception as e:
        print(f"  ⚠  Could not load sheet: {e}")
        return set(), set()


def already_in_sheet(place: dict, existing_names: set, existing_addresses: set) -> bool:
    """Return True if this place is already in the Google Sheet."""
    name    = normalize(place.get("displayName", {}).get("text", ""))
    address = normalize(place.get("formattedAddress", "").replace(", USA", ""))
    return name in existing_names or address in existing_addresses


def text_search(term: str, bounds: dict) -> list[dict]:
    """Search for a term within a bounding box, paginating through all results."""
    results    = []
    page_token = None

    while True:
        headers = {
            "X-Goog-Api-Key":   API_KEY,
            "X-Goog-FieldMask": FIELD_MASK,
            "Content-Type":     "application/json",
        }
        body = {
            "textQuery":           term,
            "locationRestriction": {"rectangle": bounds},
        }
        if page_token:
            body["pageToken"] = page_token

        resp = requests.post(SEARCH_URL, headers=headers, json=body, timeout=10)
        if not resp.ok:
            print(f"    ⚠  HTTP {resp.status_code}: {resp.text}")
            break

        data = resp.json()
        if "error" in data:
            print(f"    ⚠  API error: {data['error'].get('message', data['error'])}")
            break

        places = data.get("places", [])
        results.extend(places)

        page_token = data.get("nextPageToken")
        if not page_token:
            break
        time.sleep(2)  # required delay before using nextPageToken

    return results


def main():
    if not API_KEY:
        raise SystemExit("Error: PLACES_API_KEY environment variable is not set.")

    print("Loading existing sheet entries to skip duplicates...")
    existing_names, existing_addresses = load_existing_sheet()

    seen       = {}  # place_id → place, for deduplication across all searches
    all_places = []

    for region in REGIONS:
        print(f"\n── {region['name']} ──")
        for term in TERMS:
            print(f"  Searching: {term}")
            places = text_search(term, region["bounds"])
            new = 0
            for p in places:
                pid = p.get("id")
                if pid and pid not in seen:
                    if already_in_sheet(p, existing_names, existing_addresses):
                        seen[pid] = p  # mark as seen so we don't log it again
                        continue
                    seen[pid] = p
                    all_places.append(p)
                    new += 1
            print(f"    {new} new ({len(places)} total)")

    print(f"\n{len(all_places)} unique places found across all regions.")

    rows = []
    for place in all_places:
        name    = place.get("displayName", {}).get("text", "")
        address = place.get("formattedAddress", "").replace(", USA", "")
        phone   = place.get("nationalPhoneNumber", "")
        website = place.get("websiteUri", "")

        rows.append({
            "name":           name,
            "address":        address,
            "website":        website,
            "phone":          phone,
            "classes":        "",
            "open_studio":    "",
            "member_studios": "",
            "gallery":        "",
            "supplies":       "",
            "artist_studio":  "",
            "notes":          "",
        })

    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "name", "address", "website", "phone",
            "classes", "open_studio", "member_studios",
            "gallery", "supplies", "artist_studio", "notes",
        ])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done — {len(rows)} studios written to studios_raw.csv")
    print("Review the file, fill in the TRUE/FALSE columns, remove irrelevant rows,")
    print("then paste into your Google Sheet.")


if __name__ == "__main__":
    main()
