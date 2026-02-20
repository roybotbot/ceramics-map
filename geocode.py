#!/usr/bin/env python3
"""
geocode.py — MA Pottery Studios geocoder
Converts studio addresses to GeoJSON using Nominatim (OSM).
Run once to seed studios.json. Edit studios.json directly for ongoing updates.

Usage:
    pip3 install requests
    python3 geocode.py
"""

import json
import time
import sys
import requests

USER_AGENT = "ma-pottery-map/1.0 contact@example.com"

# ─── Studio data ──────────────────────────────────────────────────────────────
# Fields: name, address, website, phone, classes, open_studio, member_studios, notes
# classes       = teaches pottery/ceramics classes to the public
# open_studio   = members can use studio independently (open studio time)
# member_studios = run by/for member artists (co-op or collective model)

STUDIOS = [
    # ── Somerville / Cambridge ─────────────────────────────────────────────
    {
        "name": "Mudflat Studio",
        "address": "149 Broadway, Somerville, MA",
        "website": "https://mudflat.org",
        "phone": "(617) 628-0589",
        "classes": True,
        "open_studio": True,
        "member_studios": True,
        "notes": "Community ceramics studio offering classes for all levels, open studio time, and member artists. One of the oldest pottery studios in the Boston area."
    },
    {
        "name": "The Clay School",
        "address": "130 Bishop Allen Dr, Cambridge, MA",
        "website": "https://theclayschool.com",
        "phone": "",
        "classes": True,
        "open_studio": True,
        "member_studios": False,
        "notes": "Community ceramics studio in Cambridge offering wheel throwing, hand building, and glaze classes for all skill levels."
    },
    {
        "name": "Cambridge Center for Adult Education",
        "address": "42 Brattle St, Cambridge, MA",
        "website": "https://ccae.org",
        "phone": "(617) 547-6789",
        "classes": True,
        "open_studio": False,
        "member_studios": False,
        "notes": "Long-running adult education center in Harvard Square offering ceramics and pottery classes alongside other arts courses."
    },
    {
        "name": "Artisan's Asylum",
        "address": "10 Tyler St, Somerville, MA",
        "website": "https://artisansasylum.com",
        "phone": "(617) 616-6943",
        "classes": True,
        "open_studio": True,
        "member_studios": True,
        "notes": "Large maker community space with a dedicated ceramics studio. Offers classes and open studio membership."
    },
    # ── Boston ────────────────────────────────────────────────────────────
    {
        "name": "Society of Arts and Crafts",
        "address": "100 Pier 4 Blvd, Boston, MA",
        "website": "https://societyofcrafts.org",
        "phone": "(617) 266-1810",
        "classes": False,
        "open_studio": False,
        "member_studios": False,
        "notes": "America's oldest nonprofit craft organization. Gallery and shop selling handmade ceramics and other fine crafts by juried artists."
    },
    {
        "name": "MassArt Continuing Education",
        "address": "621 Huntington Ave, Boston, MA",
        "website": "https://massart.edu/continuing-education",
        "phone": "(617) 879-7000",
        "classes": True,
        "open_studio": False,
        "member_studios": False,
        "notes": "Massachusetts College of Art and Design continuing education program offering ceramics and sculpture classes to the public."
    },
    # ── Arlington / Newton / Brookline ────────────────────────────────────
    {
        "name": "Arlington Center for the Arts",
        "address": "41 Foster St, Arlington, MA",
        "website": "https://acarts.org",
        "phone": "(781) 648-6220",
        "classes": True,
        "open_studio": False,
        "member_studios": False,
        "notes": "Community arts center offering ceramics classes for adults and youth in Arlington."
    },
    {
        "name": "New Art Center",
        "address": "61 Washington Park, Newtonville, MA",
        "website": "https://newartcenter.org",
        "phone": "(617) 964-3424",
        "classes": True,
        "open_studio": True,
        "member_studios": False,
        "notes": "Community arts center in Newton offering wheel throwing, hand building, and raku ceramics classes and studio membership."
    },
    {
        "name": "Brookline Arts Center",
        "address": "86 Monmouth St, Brookline, MA",
        "website": "https://brooklineartscenter.com",
        "phone": "(617) 566-4452",
        "classes": True,
        "open_studio": False,
        "member_studios": False,
        "notes": "Community arts center offering pottery and ceramics classes for adults and children in Brookline."
    },
    # ── North Shore ───────────────────────────────────────────────────────
    {
        "name": "North Shore Art Center",
        "address": "11 Pleasant St, Marblehead, MA",
        "website": "https://northshorearts.org",
        "phone": "(781) 631-5515",
        "classes": True,
        "open_studio": False,
        "member_studios": False,
        "notes": "Arts center on the North Shore offering pottery and ceramics classes alongside fine arts instruction."
    },
    {
        "name": "Montserrat College of Art",
        "address": "23 Essex St, Beverly, MA",
        "website": "https://montserrat.edu",
        "phone": "(978) 921-4242",
        "classes": True,
        "open_studio": False,
        "member_studios": False,
        "notes": "Visual arts college offering community ceramics courses through its continuing education program."
    },
    # ── South Shore ───────────────────────────────────────────────────────
    {
        "name": "South Shore Art Center",
        "address": "119 Ripley Rd, Cohasset, MA",
        "website": "https://southshoreart.org",
        "phone": "(781) 383-2787",
        "classes": True,
        "open_studio": True,
        "member_studios": False,
        "notes": "Established arts center offering ceramics and pottery classes, open studio time, and gallery exhibitions."
    },
    # ── MetroWest ─────────────────────────────────────────────────────────
    {
        "name": "Danforth Art Museum School",
        "address": "123 Union Ave, Framingham, MA",
        "website": "https://danforthart.org",
        "phone": "(508) 620-0050",
        "classes": True,
        "open_studio": False,
        "member_studios": False,
        "notes": "Art school and museum offering ceramics and pottery classes for adults and children in Framingham."
    },
    {
        "name": "The Pottery Studio",
        "address": "84 Thoreau St, Concord, MA",
        "website": "",
        "phone": "",
        "classes": True,
        "open_studio": True,
        "member_studios": False,
        "notes": "Community pottery studio in Concord offering wheel and hand building classes and open studio membership."
    },
    # ── Worcester ─────────────────────────────────────────────────────────
    {
        "name": "Worcester Center for Crafts",
        "address": "25 Sagamore Rd, Worcester, MA",
        "website": "https://worcestercraftcenter.org",
        "phone": "(508) 753-8183",
        "classes": True,
        "open_studio": True,
        "member_studios": True,
        "notes": "One of the largest craft schools in New England. Offers extensive ceramics programming, open studio, and resident artist studios."
    },
    # ── Pioneer Valley / Western MA ───────────────────────────────────────
    {
        "name": "Northampton Center for the Arts",
        "address": "17 New South St, Northampton, MA",
        "website": "https://nohoarts.org",
        "phone": "(413) 584-7327",
        "classes": True,
        "open_studio": False,
        "member_studios": True,
        "notes": "Arts center in downtown Northampton with ceramics studio space and classes in the Pioneer Valley."
    },
    {
        "name": "Digging Dog Pottery",
        "address": "23 Mechanic St, Shelburne Falls, MA",
        "website": "https://diggingdogpottery.com",
        "phone": "",
        "classes": True,
        "open_studio": True,
        "member_studios": False,
        "notes": "Working pottery studio in Shelburne Falls offering classes and open studio. Beautiful rural setting in the Pioneer Valley."
    },
    # ── Regional (NH) ─────────────────────────────────────────────────────
    {
        "name": "Studio 550",
        "address": "550 Elm St, Manchester, NH",
        "website": "https://studio550.org",
        "phone": "(603) 668-6656",
        "classes": True,
        "open_studio": True,
        "member_studios": True,
        "notes": "Regional ceramics studio just over the NH border. Included as a resource for potters in northern MA. Classes, open studio, and member space."
    },
]

# ─── Geocoder ─────────────────────────────────────────────────────────────────

def geocode(address: str) -> tuple[float, float] | None:
    """Return (lon, lat) or None if geocoding fails."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1,
        "countrycodes": "us",
    }
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        results = resp.json()
        if results:
            lat = float(results[0]["lat"])
            lon = float(results[0]["lon"])
            return (lon, lat)
        else:
            print(f"  ⚠ No result for: {address}")
            return None
    except Exception as e:
        print(f"  ⚠ Error geocoding '{address}': {e}")
        return None


def build_geojson(studios: list[dict]) -> dict:
    features = []
    total = len(studios)

    for i, studio in enumerate(studios, 1):
        print(f"[{i}/{total}] Geocoding: {studio['name']} — {studio['address']}")
        coords = geocode(studio["address"])

        if coords is None:
            print(f"  ✗ Skipping {studio['name']}")
            continue

        lon, lat = coords
        print(f"  ✓ {lat:.5f}, {lon:.5f}")

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "properties": {
                "name": studio["name"],
                "address": studio["address"],
                "website": studio.get("website", ""),
                "phone": studio.get("phone", ""),
                "classes": studio.get("classes", False),
                "open_studio": studio.get("open_studio", False),
                "member_studios": studio.get("member_studios", False),
                "notes": studio.get("notes", ""),
            }
        }
        features.append(feature)

        if i < total:
            time.sleep(1)  # Nominatim rate limit: max 1 req/sec

    return {
        "type": "FeatureCollection",
        "features": features
    }


def main():
    print(f"MA Pottery Studios Geocoder")
    print(f"Processing {len(STUDIOS)} studios...\n")

    geojson = build_geojson(STUDIOS)

    output_path = "studios.json"
    with open(output_path, "w") as f:
        json.dump(geojson, f, indent=2)

    success = len(geojson["features"])
    failed = len(STUDIOS) - success
    print(f"\nDone. {success} studios written to {output_path}")
    if failed:
        print(f"  {failed} studios failed geocoding — check addresses above")


if __name__ == "__main__":
    main()
