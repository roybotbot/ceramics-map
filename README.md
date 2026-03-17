# Massachusetts Ceramics Map

An interactive map of 170 pottery and ceramics studios across Massachusetts. Search by name, filter by category, tap for details.

**Live at [roysclay.co/ceramics-map/](https://roysclay.co/ceramics-map/)**

---

## Adding a Studio

### Option 1: Pull request (preferred)

1. Fork this repo
2. Add an entry to `studios.json` (copy an existing one):

```json
{
  "type": "Feature",
  "geometry": { "type": "Point", "coordinates": [-71.0890, 42.3885] },
  "properties": {
    "name": "Studio Name",
    "address": "123 Main St, City, MA 01234",
    "website": "https://example.com",
    "phone": "(555) 555-5555",
    "classes": true,
    "open_studio": false,
    "member_studios": false,
    "gallery": false,
    "supplies": false,
    "artist_studio": false,
    "notes": "Short description."
  }
}
```

3. Open a pull request

**Coordinate order is `[longitude, latitude]`** — longitude first (GeoJSON standard). Find coordinates at [nominatim.openstreetmap.org](https://nominatim.openstreetmap.org). If you don't know the coordinates, put `[0, 0]` and we'll geocode it.

### Option 2: Open an issue

Use the [Add a Studio](../../issues/new?template=add-studio.yml) issue template. Fill in the details and we'll add it.

### Option 3: Google Form

Coming soon — a simple form for non-technical submissions.

---

## Property Reference

| Property | Type | Meaning |
|---|---|---|
| `classes` | boolean | Teaches pottery/ceramics classes |
| `open_studio` | boolean | Members can use the studio independently |
| `member_studios` | boolean | Co-op or collective run by member artists |
| `gallery` | boolean | Has a gallery showing ceramics work |
| `supplies` | boolean | Sells pottery supplies or clay |
| `artist_studio` | boolean | Individual artist's working studio |

A studio should have at least one category set to `true`.

---

## Running Locally

`fetch()` won't work over `file://` URLs. Use a local server:

```bash
python3 -m http.server 8000
```

Open **http://localhost:8000**.

---

## Scripts

| Script | Purpose |
|---|---|
| `sheets_to_json.py` | Imports new entries from a Google Sheet into `studios.json` |
| `check_urls.py` | Checks every studio website URL for dead links |
| `scrape_places.py` | Google Places API scraper for discovering new studios |
| `geocode.py` | Bulk geocoder using Nominatim (OpenStreetMap) |

---

## Stack

- [Leaflet.js](https://leafletjs.com/) 1.9.4 — map rendering
- [Leaflet.markercluster](https://github.com/Leaflet/Leaflet.markercluster) 1.5.3 — marker clustering
- [CartoDB Positron](https://carto.com/basemaps/) — light map tiles (free, no API key)
- [Space Grotesk](https://fonts.google.com/specimen/Space+Grotesk) — typography
- No build step, no framework, no backend

---

## TODO

- [x] Move scripts to `scripts/` directory, update paths
- [x] Write `CONTRIBUTING.md`
- [x] Write `validate.py` (JSON schema, coordinate bounds, duplicate check)
- [x] `validate-pr.yml` — validate `studios.json` on PRs
- [x] `check-urls.yml` — weekly dead link check
- [x] Create GitHub Issue template (`add-studio.yml`)
- [x] Create PR template
- [x] Fix favicon path — bundled `favicon.svg` in repo
- [x] Add "Add it here" link to map sidebar
- [x] Sync `--accent` color to `oklch(48%)` (matches roysclay.co contrast fix)
- [x] Fix `check_urls.py` path from `ceramics-map/studios.json` → `studios.json`
- [ ] `import-sheet-submissions.yml` — Google Sheet → PR pipeline
- [ ] Deploy action to push to roysclay.co on merge
- [ ] Set up Google Form for non-technical submissions (Roy)
- [ ] Update `sheets_to_json.py` to create PRs instead of direct commits
- [ ] Remove `ceramics-map/` from `roysclayco-website` after standalone deploy works

### Backlog

- [ ] "Find studios near me" — input your address, drop a marker, see nearby studios

---

## Docs

- [`docs/plan-standalone-repo.md`](docs/plan-standalone-repo.md) — full plan for the repo split and community submissions
- [`docs/site-updates-and-migration.md`](docs/site-updates-and-migration.md) — what changed on roysclay.co, file-by-file migration guide
- [`docs/handoff.md`](docs/handoff.md) — project context and current state

---

## License

Data in `studios.json` is community-contributed. Code is MIT.
