# Ceramics Map — Standalone Repo Plan

**Date:** 2026-03-09  
**Goal:** Split the ceramics map into its own public GitHub repo so the community can contribute studios via pull requests, while also supporting non-technical potters who can't use Git.

---

## Current State

The ceramics map lives in two places:

1. **`roybotbot/ceramics-map`** — The original standalone repo. Has 18 studios, older `index.html`, `geocode.py`. No automation.
2. **`roybotbot/roysclayco-website/ceramics-map/`** — The production version deployed under roysclay.co. Has 170 studios, updated UI with filters, `sheets_to_json.py`, `scrape_places.py`, `check_urls.py`, GitHub Actions for daily Google Sheets sync and weekly URL checks, plus `ma-boundary.geojson`.

The production version is what matters. The standalone repo needs to be updated to match it, then become the canonical home.

---

## Architecture

### Submission paths (two doors, one destination)

```
┌─────────────────────────┐     ┌─────────────────────────┐
│   Technical contributor │     │   Non-technical potter   │
│                         │     │                          │
│  Fork → edit studios.json    │  Fill out Google Form     │
│  or studios.csv → PR    │     │  (name, address, URL,    │
│                         │     │   what they offer)       │
└────────────┬────────────┘     └────────────┬─────────────┘
             │                               │
             │  Pull Request                 │  Form → Google Sheet
             │                               │  (reviewed by Roy)
             ▼                               ▼
     ┌───────────────┐              ┌─────────────────┐
     │  GitHub repo   │◄────sync────│  Google Sheet    │
     │  studios.json  │             │  (source of truth│
     └───────┬───────┘              │   for form subs) │
             │                      └─────────────────┘
             │  GitHub Action
             │  (build + deploy)
             ▼
     ┌───────────────┐
     │  roysclay.co   │
     │  /ceramics-map/ │
     └───────────────┘
```

### Why two paths?

Most potters will never touch GitHub. A Google Form that feeds a Sheet is familiar and zero-friction. But technical people (developers, data folks) should be able to submit PRs directly against `studios.json` — it's a GeoJSON file, easy to edit.

The key design decision: **which is the source of truth?**

### Option A: Google Sheet is source of truth (current approach)
- Sheet syncs → `studios.json` daily via GitHub Action
- PRs edit `studios.json` directly, and get manually back-synced to the Sheet
- Risk: PR edits get overwritten by the next Sheet sync if not added to the Sheet

### Option B: `studios.json` is source of truth (recommended)
- PRs edit `studios.json` directly — this is the canonical data
- Google Form submissions go to a Sheet, which is a staging area
- A GitHub Action (or manual review) merges new Sheet entries into `studios.json`
- Sheet is append-only; never overwrites `studios.json`
- Avoids the overwrite problem entirely

### Recommendation: Option B

The repo's `studios.json` is the source of truth. The Sheet is an inbox for non-technical submissions. A script (or Action) proposes new Sheet entries as PRs, which Roy reviews and merges.

---

## Repo Structure (new)

```
ceramics-map/
├── index.html              # Full map app (single file)
├── studios.json            # Source of truth — all studio data (GeoJSON)
├── ma-boundary.geojson     # State outline overlay
├── .htaccess               # CORS headers for JSON
├── .gitignore
│
├── scripts/
│   ├── geocode.py          # Geocode addresses → coordinates
│   ├── sheets_to_json.py   # Import new entries from Google Sheet → PR
│   ├── scrape_places.py    # Google Places API scraper (for discovery)
│   ├── check_urls.py       # Weekly dead link checker
│   └── validate.py         # NEW: validate studios.json schema + coords
│
├── .github/
│   ├── workflows/
│   │   ├── import-sheet-submissions.yml  # Sheet → PR (replaces direct sync)
│   │   ├── check-urls.yml                # Weekly URL health check
│   │   └── validate-pr.yml              # NEW: validate studios.json on PR
│   ├── ISSUE_TEMPLATE/
│   │   └── add-studio.yml               # NEW: issue template for submissions
│   └── PULL_REQUEST_TEMPLATE.md          # NEW: PR checklist
│
├── CONTRIBUTING.md          # NEW: how to add a studio (both paths)
├── README.md                # Updated project overview
└── docs/
    └── plans/
        └── ...
```

---

## Submission Flow: Pull Requests

### For contributors who know Git

1. Fork the repo
2. Edit `studios.json` — add a new feature block (copy an existing one)
3. Open a PR
4. GitHub Action runs `validate-pr.yml`:
   - Checks JSON is valid
   - Checks required fields are present (name, address, at least one boolean true)
   - Checks coordinates are within Massachusetts bounding box
   - Checks for duplicate addresses
5. Roy reviews and merges

### CONTRIBUTING.md should include:
- Exact JSON template to copy-paste
- How to find coordinates (link to nominatim.openstreetmap.org)
- Property reference table (what each boolean means)
- Example of a complete entry
- Note: if you don't know the coordinates, just put `[0, 0]` and we'll geocode it

---

## Submission Flow: Google Form (non-technical)

### Setup
1. Create a Google Form with fields:
   - Studio name (required)
   - Street address, city, state, zip (required)
   - Website URL (optional)
   - Phone (optional)
   - Checkboxes: Classes, Open Studio, Member Studios, Gallery, Supplies, Artist Studio
   - Notes / description (optional)
   - Submitter name / email (optional, for follow-up)

2. Form responses go to a Google Sheet (the same one or a new "submissions" sheet)

3. Sheet is published as CSV (existing pattern from `sheets_to_json.py`)

### Automation
- `import-sheet-submissions.yml` runs daily (or on-demand)
- Reads the submissions Sheet
- Compares against existing `studios.json` (by name + address fuzzy match)
- For each new entry: geocodes, validates, creates a branch + PR
- PR title: "Add studio: [Studio Name]"
- PR body: shows the entry details for Roy to review
- Roy reviews, merges or closes

### Why PRs instead of direct commits?
- Roy maintains quality control (fake entries, duplicates, wrong data)
- Each addition has a clear audit trail
- Contributors can be credited in the commit history

---

## Validation Script (`validate.py`)

Runs on every PR that touches `studios.json`:

```python
# Checks:
# 1. Valid JSON
# 2. Valid GeoJSON FeatureCollection
# 3. Every feature has required properties
# 4. Coordinates are [lon, lat] within MA bounding box:
#    lat: 41.0–43.0, lon: -73.6–-69.8
# 5. No duplicate addresses (normalized)
# 6. At least one category boolean is true
# 7. Website URLs are well-formed (if present)
```

---

## GitHub Issue Template

For people who don't want to edit JSON but can open an issue:

```yaml
name: Add a Studio
description: Submit a ceramics studio to be added to the map
labels: [new-studio]
body:
  - type: input
    id: name
    attributes:
      label: Studio name
    validations:
      required: true
  - type: input
    id: address
    attributes:
      label: Full address
      placeholder: "123 Main St, Springfield, MA 01101"
    validations:
      required: true
  - type: input
    id: website
    attributes:
      label: Website URL
  - type: checkboxes
    id: offerings
    attributes:
      label: What does this studio offer?
      options:
        - label: Classes
        - label: Open studio time
        - label: Member studios
        - label: Gallery
        - label: Supplies
        - label: Artist studio
  - type: textarea
    id: notes
    attributes:
      label: Anything else?
```

This gives a third submission path: GitHub Issue → Roy manually adds it.

---

## Deployment

The map should continue to be served at `roysclay.co/ceramics-map/`. Two options:

### Option A: Git submodule
- `roysclayco-website` adds `ceramics-map` as a submodule at `ceramics-map/`
- When `ceramics-map` repo updates, bump the submodule ref
- Pro: clean separation. Con: submodule management is annoying.

### Option B: Deploy hook / copy (simpler)
- `ceramics-map` repo has its own deploy Action
- On push to `main`, it copies `index.html`, `studios.json`, and `ma-boundary.geojson` to the roysclay.co server (SFTP or rsync)
- Pro: simple, independent. Con: two deploy mechanisms.

### Option C: Redirect + standalone hosting
- `roysclay.co/ceramics-map/` redirects (or proxies) to a separate host (GitHub Pages, Cloudflare Pages, etc.)
- The standalone repo deploys to that host directly
- Pro: fully independent. Con: URL change or proxy complexity.

### Recommendation: Option B or C
Option B is the least disruptive — keep the existing URL, add a deploy Action to the new repo that pushes to roysclay.co. The existing `gitautodeploy.php` in roysclayco-website already handles webhook-triggered deploys, so this could be a webhook from the ceramics-map repo.

---

## Migration Steps

1. Update `ceramics-map` repo with all production files from `roysclayco-website/ceramics-map/`
2. Restructure into the layout above (move scripts to `scripts/`)
3. Add `CONTRIBUTING.md`, issue template, PR template, validation script
4. Add GitHub Actions (`validate-pr.yml`, `import-sheet-submissions.yml`)
5. Set up the Google Form + link it to a submissions Sheet
6. Update README with contribution instructions and form link
7. Set up deploy Action to push to roysclay.co
8. Remove `ceramics-map/` from `roysclayco-website` (replace with redirect or deploy target)
9. Link the new repo from the map's sidebar footer ("Contribute on GitHub")
10. Announce on Instagram / pottery communities

---

## Open Questions

- **Scope expansion?** Currently MA-only. Should the repo/form support other states eventually? If so, the validation bounding box and file structure might need to anticipate that.
- **Moderation?** If the form gets spam, may need a simple approval workflow (Sheet column for "approved" status, only approved entries get PR'd).
- **Attribution?** Should contributors be credited somewhere on the map? A "Contributors" section in README is easy.
- **Google Sheet URL exposure?** The published Sheet CSV URL is semi-public. Form submissions sheet should be separate from any curated data to avoid tampering.
