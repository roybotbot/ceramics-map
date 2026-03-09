# Handoff: Ceramics Map Project

**Date:** 2026-03-09  
**From:** Claude Code session with Roy  
**For:** Next Claude Code session picking up this work

---

## What is this?

A web map of ceramics/pottery studios in Massachusetts. Static site — Leaflet.js map, GeoJSON data, no backend. Currently lives at [roysclay.co/ceramics-map/](https://roysclay.co/ceramics-map/) as part of Roy's pottery website.

Roy wants to split it into its own public GitHub repo so the pottery community can contribute studios.

---

## Repos

### `roybotbot/roysclayco-website` (roysclay.co)
- **Local path:** `~/Projects/roysclayco-website/`
- Roy's personal pottery site. The ceramics map lives at `ceramics-map/` subdirectory.
- **This is where the production code is.** 170 studios, updated UI with category filters, Google Sheets sync, URL health checks.
- Two recent branches were merged to `main` and pushed (2026-03-04 and 2026-03-09):
  - `improvements` — meta tags, image optimization, lightbox keyboard nav, filter fix, 404 page, sitemap, robots.txt
  - `lighthouse-mobile-fixes` — WebP images, non-blocking fonts, CLS fixes, color contrast, `<main>` landmark

### `roybotbot/ceramics-map` (the standalone repo)
- **Local path:** `~/Projects/ceramics-map/`
- The original standalone repo. **Outdated** — only 18 studios, older UI, no automation.
- This is the repo that will become the canonical home for the ceramics map.
- I created three planning docs in `docs/` (described below) but did NOT push them.

---

## Current state of `~/Projects/ceramics-map/`

```
ceramics-map/
├── .git/                    # Points to roybotbot/ceramics-map on GitHub
├── .htaccess                # CORS headers
├── docs/
│   ├── plans/
│   │   └── 2026-02-20-pottery-map-design.md   # Original design plan (dark UI, outdated)
│   ├── plan-standalone-repo.md                 # NEW — plan for the split + community submissions
│   ├── site-updates-and-migration.md           # NEW — what changed on roysclay.co, migration steps
│   └── handoff.md                              # NEW — this file
├── geocode.py               # Geocoder script
├── index.html               # OLD version (18 studios, no filters, different design)
├── README.md                # OLD — references Dark Mono UI, VT323 font (no longer used)
└── studios.json             # OLD — only 18 studios
```

### What's NOT here yet (needs to come from roysclayco-website)
- The 170-studio `studios.json`
- The production `index.html` (with category filters)
- `ma-boundary.geojson`
- `sheets_to_json.py`
- `scrape_places.py`
- `check_urls.py`
- GitHub Actions workflows

---

## The plan (read `docs/plan-standalone-repo.md` for full detail)

1. **Copy production files** from `~/Projects/roysclayco-website/ceramics-map/` into this repo
2. **Restructure:** move scripts to `scripts/`, update paths
3. **Source of truth:** `studios.json` in the repo becomes canonical. Google Sheet becomes a staging inbox for non-technical submissions (not a direct sync).
4. **Three submission paths for adding studios:**
   - **Pull request:** Technical users edit `studios.json` directly
   - **Google Form:** Non-technical potters fill out a form → Sheet → automated PR
   - **GitHub Issue:** Template-based issue for people who can open issues but not PRs
5. **Validation:** GitHub Action on PRs checks JSON schema, coordinates in MA, no duplicates
6. **Deploy:** Action pushes to roysclay.co/ceramics-map/ on merge to main
7. **Remove** ceramics-map directory from roysclayco-website after standalone deploy works

---

## Key files in roysclayco-website/ceramics-map/ to understand

| File | What it does |
|------|-------------|
| `studios.json` | 170 studios in GeoJSON. **The valuable data.** |
| `index.html` | Full map app. Leaflet + MarkerCluster. Sidebar with search + 6 category filter checkboxes. Mobile drawer. ~940 lines. |
| `ma-boundary.geojson` | Massachusetts state boundary polygon. Drawn as a subtle overlay on the map. |
| `sheets_to_json.py` | Fetches a public Google Sheet CSV, geocodes new addresses, writes `studios.json`. Currently runs as a daily GitHub Action that commits directly. Will need to be changed to create PRs instead. |
| `check_urls.py` | Checks every studio website URL. Opens/updates a GitHub issue if dead links found. Runs weekly. Path hardcoded to `ceramics-map/studios.json` — needs to be `studios.json` after move. |
| `scrape_places.py` | Google Places API scraper for discovering new studios. Outputs `studios_raw.csv`. Manual tool, not automated. |
| `geocode.py` | Bulk geocoder using Nominatim. Reads addresses, outputs coordinates. Used by `sheets_to_json.py` internally. |

---

## Important technical details

- **Coordinate order in studios.json:** `[longitude, latitude]` (GeoJSON standard, opposite of what most people expect)
- **Google Sheet sync:** Uses a `SHEET_URL` stored as a GitHub Actions variable (not secret). The Sheet is published as CSV.
- **Geocoding:** Nominatim (OpenStreetMap) with 1 req/sec rate limit. `sheets_to_json.py` caches coordinates from existing `studios.json` to avoid re-geocoding known addresses.
- **The index.html has inline CSS and JS** — no build step, no external CSS/JS files (other than Leaflet + MarkerCluster CDN). This is intentional — keep it simple.
- **Filter logic:** A studio shows on the map if `nameMatch AND (at least one checked filter category is true on the studio)`. If no filters checked, nothing shows.
- **The ceramics map's `--accent` color is still the old `#c66b3b` / `oklch(58%)`** — the main site darkened it to `oklch(48%)` for contrast. You may want to sync these.

---

## What Roy cares about

- The map is a community resource. He wants potters to be able to add their studios easily.
- Most potters are not technical. The Google Form path is critical.
- Data quality matters — he wants to review submissions before they go live (hence PRs, not direct adds).
- The URL should stay at `roysclay.co/ceramics-map/`.
- Keep it simple. No frameworks, no build steps, no databases.

---

## What to do next

The immediate work is the migration. Suggested order:

1. Read `docs/plan-standalone-repo.md` for the full plan
2. Read `docs/site-updates-and-migration.md` for the file-by-file migration guide
3. Copy production files from `~/Projects/roysclayco-website/ceramics-map/` to this repo
4. Restructure (move scripts to `scripts/`, update README)
5. Write `CONTRIBUTING.md`
6. Write `validate.py`
7. Set up GitHub Actions (`validate-pr.yml`, `import-sheet-submissions.yml`, `check-urls.yml`)
8. Create the GitHub Issue template (`add-studio.yml`)
9. Set up the Google Form (Roy needs to do this part — it's on his Google account)
10. Set up deploy Action to push to roysclay.co
11. Test the full flow end-to-end
12. Remove `ceramics-map/` from `roysclayco-website`

---

## Files I created this session (not yet committed or pushed)

```
~/Projects/ceramics-map/docs/plan-standalone-repo.md
~/Projects/ceramics-map/docs/site-updates-and-migration.md
~/Projects/ceramics-map/docs/handoff.md          # ← this file
```

These are local only. Commit and push when ready.
