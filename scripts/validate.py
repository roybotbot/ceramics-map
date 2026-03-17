"""
validate.py — validate studios.json schema, coordinates, and duplicates

Checks:
  1. Valid JSON
  2. Valid GeoJSON FeatureCollection
  3. Every feature has required properties
  4. Coordinates are [lon, lat] within Massachusetts bounding box
  5. No duplicate addresses (normalized)
  6. At least one category boolean is true per studio
  7. Website URLs are well-formed (if present)
  8. Address format (street number, city, state — enough for geocoding)

Exit codes:
  0 — all checks pass
  1 — one or more checks failed
"""

import json
import os
import re
import sys
from urllib.parse import urlparse

REPO_ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDIOS_FILE = os.path.join(REPO_ROOT, "studios.json")

# Massachusetts bounding box (with a small buffer)
MA_LAT_MIN, MA_LAT_MAX = 41.0, 43.0
MA_LON_MIN, MA_LON_MAX = -73.6, -69.8

REQUIRED_PROPS = ["name", "address"]
CATEGORY_BOOLS = [
    "classes", "open_studio", "member_studios",
    "gallery", "supplies", "artist_studio",
]


def normalize_address(addr):
    """Normalize an address for duplicate detection."""
    addr = addr.lower().strip()
    addr = re.sub(r"\s+", " ", addr)
    # Normalize common abbreviations
    for full, abbr in [
        ("street", "st"), ("avenue", "ave"), ("drive", "dr"),
        ("road", "rd"), ("boulevard", "blvd"), ("lane", "ln"),
        ("court", "ct"), ("place", "pl"),
    ]:
        addr = re.sub(rf"\b{full}\b", abbr, addr)
        addr = re.sub(rf"\b{abbr}\.\b", f"{abbr}", addr)
    # Remove trailing punctuation
    addr = re.sub(r"[.,]+$", "", addr)
    return addr


US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC",
}


def check_address_format(addr):
    """Check if an address has enough structure for geocoding.

    Returns a list of warning strings (empty if address looks fine).
    Expected format: '123 Main St, City, STATE 01234'
    """
    issues = []

    # Must have at least one comma (separating street from city)
    if "," not in addr:
        issues.append("no commas — expected 'Street, City, State Zip'")
        return issues  # Can't check further if no structure at all

    parts = [p.strip() for p in addr.split(",")]

    # Check street part has a number somewhere (allow building name prefix)
    street = parts[0]
    # Look for a number in any comma-separated part before the city
    has_number = any(re.search(r"\d", p) for p in parts[:-1])
    if not has_number:
        issues.append("no street number found")

    # Check for state abbreviation
    has_state = bool(re.search(r"\b(" + "|".join(US_STATES) + r")\b", addr))
    if not has_state:
        issues.append("no state abbreviation found")

    # Check for zip code (warning only — geocoding often works without it)
    has_zip = bool(re.search(r"\b\d{5}\b", addr))
    if not has_zip:
        issues.append("no zip code")

    return issues


def validate():
    errors = []
    warnings = []

    # 1. Read and parse JSON
    try:
        with open(STUDIOS_FILE) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON: {e}")
        return errors, warnings
    except FileNotFoundError:
        errors.append(f"File not found: {STUDIOS_FILE}")
        return errors, warnings

    # 2. Check GeoJSON structure
    if data.get("type") != "FeatureCollection":
        errors.append(f'Top-level "type" must be "FeatureCollection", got: {data.get("type")}')
        return errors, warnings

    features = data.get("features", [])
    if not features:
        errors.append("No features found")
        return errors, warnings

    seen_addresses = {}

    for i, feat in enumerate(features):
        label = f"Feature #{i}"
        props = feat.get("properties", {})
        name = props.get("name", "???")
        label = f'"{name}" (#{i})'

        # Check feature type
        if feat.get("type") != "Feature":
            errors.append(f"{label}: type must be 'Feature', got '{feat.get('type')}'")

        # 3. Check required properties
        for prop in REQUIRED_PROPS:
            val = props.get(prop, "")
            if not val or not str(val).strip():
                errors.append(f"{label}: missing required property '{prop}'")

        # 4. Check coordinates
        geom = feat.get("geometry", {})
        if geom.get("type") != "Point":
            errors.append(f"{label}: geometry type must be 'Point', got '{geom.get('type')}'")
        else:
            coords = geom.get("coordinates", [])
            if len(coords) < 2:
                errors.append(f"{label}: coordinates must be [lon, lat]")
            else:
                lon, lat = coords[0], coords[1]

                # Allow [0, 0] as "unknown, will geocode"
                if lon == 0 and lat == 0:
                    warnings.append(f"{label}: coordinates are [0, 0] — needs geocoding")
                elif not (MA_LAT_MIN <= lat <= MA_LAT_MAX):
                    warnings.append(
                        f"{label}: latitude {lat} outside MA range "
                        f"({MA_LAT_MIN}–{MA_LAT_MAX})"
                    )
                elif not (MA_LON_MIN <= lon <= MA_LON_MAX):
                    warnings.append(
                        f"{label}: longitude {lon} outside MA range "
                        f"({MA_LON_MIN}–{MA_LON_MAX})"
                    )

        # 5. Check for duplicate addresses
        addr = props.get("address", "")
        if addr:
            norm = normalize_address(addr)
            if norm in seen_addresses:
                warnings.append(
                    f"{label}: duplicate address with "
                    f'"{seen_addresses[norm]}" — "{addr}"'
                )
            else:
                seen_addresses[norm] = name

        # 6. Check address format
        if addr:
            addr_issues = check_address_format(addr)
            for issue in addr_issues:
                # Missing state or no commas is an error (geocoding will fail)
                # Missing number or zip is a warning (geocoding might still work)
                if "no commas" in issue or "no state" in issue:
                    errors.append(f"{label}: address — {issue}")
                else:
                    warnings.append(f"{label}: address — {issue}")

        # 7. Check at least one category boolean is true
        bools = [props.get(b, False) for b in CATEGORY_BOOLS]
        if not any(bools):
            warnings.append(f"{label}: no category booleans are true")

        # 8. Check website URL format
        website = props.get("website", "")
        if website:
            parsed = urlparse(website)
            if parsed.scheme not in ("http", "https"):
                errors.append(f"{label}: website must start with http:// or https://, got '{website}'")
            elif not parsed.netloc:
                errors.append(f"{label}: website has no domain: '{website}'")

    return errors, warnings


def main():
    errors, warnings = validate()

    for w in warnings:
        print(f"⚠  {w}")
    for e in errors:
        print(f"✗  {e}")

    total_features = 0
    try:
        with open(STUDIOS_FILE) as f:
            total_features = len(json.load(f).get("features", []))
    except Exception:
        pass

    print(f"\n{'─' * 50}")
    print(f"Studios: {total_features}")
    print(f"Errors:  {len(errors)}")
    print(f"Warnings: {len(warnings)}")

    if errors:
        print("\n✗ Validation FAILED")
        sys.exit(1)
    else:
        print("\n✓ Validation passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
