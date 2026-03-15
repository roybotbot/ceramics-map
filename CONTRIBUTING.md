# Contributing a Studio

There are three ways to add a ceramics studio to the map.

---

## Option 1: Pull request (if you know Git)

1. Fork this repo
2. Add a new entry to `studios.json` — copy an existing block and fill in the values:

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

### Finding coordinates

Go to [nominatim.openstreetmap.org](https://nominatim.openstreetmap.org), search the address, and use the lat/lon shown. **Coordinate order is `[longitude, latitude]`** — longitude first (GeoJSON standard).

If you don't know the coordinates, put `[0, 0]` and we'll geocode it.

### Validation

Run the validator locally before opening your PR:

```bash
python3 scripts/validate.py
```

### Property reference

| Property | Type | Meaning |
|---|---|---|
| `classes` | boolean | Teaches pottery/ceramics classes |
| `open_studio` | boolean | Members can use the studio independently |
| `member_studios` | boolean | Co-op or collective run by member artists |
| `gallery` | boolean | Has a gallery showing ceramics work |
| `supplies` | boolean | Sells pottery supplies or clay |
| `artist_studio` | boolean | Individual artist's working studio |

Set at least one to `true`. If you're not sure, your best guess is fine — we can fix it.

---

## Option 2: Open a GitHub Issue

Use the **[Add a Studio](../../issues/new?template=add-studio.yml)** issue template. Fill in what you know and we'll take it from there.

---

## Option 3: Google Form

Coming soon — a simple form for non-technical submissions.

---

## Updating or removing a studio

If a studio has closed, moved, or has incorrect information, please [open an issue](../../issues/new) with the details. Or submit a PR editing the entry in `studios.json`.

---

## Code of conduct

Be helpful, be accurate, be kind. This is a community resource for potters.
