# MA Pottery Studios

A static map of pottery studios, schools, and galleries in Massachusetts. Built with Leaflet.js + CartoDB dark tiles. No backend, no build step.

---

## Running locally

`fetch()` doesn't work over `file://` URLs (CORS). You need a local server. Pick any one:

```bash
# Python (built in — recommended)
python3 -m http.server 8000

# Node (if installed)
npx serve .

# PHP (if installed)
php -S localhost:8000
```

Then open **http://localhost:8000** in your browser.

---

## Re-geocoding studios

The `studios.json` file is the source of truth. `geocode.py` is for bulk re-geocoding only.

```bash
pip3 install requests
python3 geocode.py
```

This hits Nominatim (OSM's free geocoder) — takes ~20 seconds due to the mandatory 1-second rate limit between requests.

---

## Adding a new studio

Edit `studios.json` directly. Copy an existing feature block and fill in the values:

```json
{
  "type": "Feature",
  "geometry": { "type": "Point", "coordinates": [-71.0890, 42.3885] },
  "properties": {
    "name": "Studio Name",
    "address": "123 Main St, City, MA",
    "website": "https://example.com",
    "phone": "(555) 555-5555",
    "classes": true,
    "open_studio": false,
    "member_studios": false,
    "notes": "Short description of the studio."
  }
}
```

**Coordinate order:** `[longitude, latitude]` — longitude first (common GeoJSON gotcha).

To find coordinates for an address: go to [nominatim.openstreetmap.org](https://nominatim.openstreetmap.org), search the address, click the result, and use the lat/lon shown.

---

## Property reference

| Property | Type | Meaning |
|---|---|---|
| `classes` | boolean | Teaches pottery/ceramics classes to the public |
| `open_studio` | boolean | Members can use the studio independently |
| `member_studios` | boolean | Run by/for member artists (co-op or collective) |

---

## Deploy to Cloudways

See `docs/plans/2026-02-20-pottery-map-design.md` for full Cloudways deployment instructions (SFTP, Git, rsync options).

Short version: upload `index.html` + `studios.json` to your app's `public_html` folder via SFTP.

---

## Stack

- [Leaflet.js](https://leafletjs.com/) 1.9.4 — map rendering
- [Leaflet.markercluster](https://github.com/Leaflet/Leaflet.markercluster) 1.5.3 — marker clustering
- [CartoDB Dark Matter](https://carto.com/basemaps/) — dark map tiles (free, no API key)
- [VT323](https://fonts.google.com/specimen/VT323) + [Inter](https://fonts.google.com/specimen/Inter) — typography
- Dark Mono Digital UI system — design language
