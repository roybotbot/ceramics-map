# Site Updates & Migration Guide

**Date:** 2026-03-09  
**Context:** What changed on roysclay.co recently, and what needs to happen to split the ceramics map into its own repo.

---

## Recent Changes to roysclay.co (2026-03-04 and 2026-03-09)

Two rounds of improvements were merged to `main` on the `roysclayco-website` repo:

### Round 1: General improvements (`improvements` branch)

**index.html:**
- Added `<meta description>`, Open Graph, and Twitter Card tags
- Font preconnect hints (`fonts.googleapis.com`, `fonts.gstatic.com`)
- `loading="lazy"` on gallery images 2–11
- `rel="noopener noreferrer"` on all `target="_blank"` links
- Copyright updated from 2025 → 2026
- Footer now links to `/ceramics-map/` ("MA Ceramics Map")
- Lightbox rewritten: Escape key, Left/Right arrow navigation, focus trap, `aria-modal`, body scroll lock

**ceramics-map/index.html:**
- Filter checkboxes restored (Classes, Open Studio, Member Studios, Gallery, Supplies, Artist Studio)
- `applyFilters()` rewritten to check active filters — studios show if they match search AND have ≥1 checked category
- Checkboxes wired to trigger filter updates

**Gallery images:**
- All 11 JPEGs resized from ~19MB total to ~1.5MB (max 1200px dimension via `sips`)

**New files:**
- `404.html` — custom 404 page matching site design
- `sitemap.xml` — entries for `/` and `/ceramics-map/`
- `robots.txt` — allows all, disallows `/archive/`, points to sitemap

### Round 2: Lighthouse mobile fixes (`lighthouse-mobile-fixes` branch)

**index.html:**
- Google Fonts made non-render-blocking (`media="print" onload="this.media='all'"` + `<noscript>` fallback)
- All gallery images wrapped in `<picture>` elements with WebP sources and JPEG fallback
- Explicit `width` and `height` on all images (eliminates CLS 0.29)
- Logo resized from 795×238 to 401×120, WebP version created (8KB)
- `<picture>` elements use `display: contents` for seamless grid layout
- Lightbox JS updated to use `.closest(".gallery-item")` for caption lookup (needed because `<img>` is now inside `<picture>`)
- `<main>` landmark added wrapping header through bio section
- Color contrast fixed:
  - `--accent` darkened from `#c66b3b` / `oklch(58%)` to `#a8552b` / `oklch(48%)` (~4.8:1 ratio on white)
  - Bio section uses lighter accent `#d4885e` / `oklch(66%)` for sufficient contrast on dark `--accent-2` background
  - Bio paragraph opacity bumped from 0.85 → 0.9

**New files:**
- 11 `.webp` gallery images (~388KB total vs ~1.5MB JPEG)
- `assets/img/logo.webp` (8KB)

---

## What Needs to Change for the Ceramics Map Split

### Files to move from `roysclayco-website/ceramics-map/` → standalone repo

| File | Notes |
|------|-------|
| `index.html` | The production version with filters. **Needs edits** (see below) |
| `studios.json` | 170 studios — this is the valuable data |
| `ma-boundary.geojson` | State outline overlay |
| `sheets_to_json.py` | Modify to create PRs instead of direct commits |
| `scrape_places.py` | Keep as-is, useful for discovery |
| `check_urls.py` | Move, update path from `ceramics-map/studios.json` → `studios.json` |
| `geocode.py` | Already exists in standalone repo, but roysclay version may be newer |
| `.htaccess` | Keep for CORS |

### Files that stay in `roysclayco-website`

| File | Notes |
|------|-------|
| `sitemap.xml` | Update if ceramics map URL changes |
| `index.html` (root) | Footer link to `/ceramics-map/` stays |
| `robots.txt` | No change needed |
| `.github/workflows/sync-studios.yml` | Delete (moving to ceramics-map repo) |
| `.github/workflows/check-studio-urls.yml` | Delete (moving to ceramics-map repo) |

### Changes needed in `ceramics-map/index.html`

1. **Header back link:** Currently points to `https://roysclay.co`. Keep this — it's correct whether hosted standalone or as a subdirectory.

2. **Asset paths:** The favicon currently uses `../assets/img/favicon.svg` (relative to subdirectory). For standalone hosting, either:
   - Bundle a favicon in the ceramics-map repo
   - Or use an absolute URL: `https://roysclay.co/assets/img/favicon.svg`

3. **Matomo tracking:** Currently tracks as site ID 3 on `matomo.roy.wtf`. Decide whether to keep tracking under the same site ID or create a separate one.

4. **Add GitHub link:** In the sidebar footer, add a "Contribute on GitHub" link pointing to the new repo.

5. **Add Google Form link:** In the sidebar footer, add "Submit a studio" linking to the Google Form.

6. **Color contrast:** The roysclay.co root page darkened `--accent` to `oklch(48%)`. The ceramics map's `index.html` still uses the old `oklch(58%)`. Sync this if you want consistency (though the map has less small text in the accent color, so it may not fail Lighthouse).

### Changes needed in scripts

1. **`check_urls.py`:** Line 21 references `"ceramics-map/studios.json"`. Change to `"studios.json"` since it'll be at the repo root.

2. **`sheets_to_json.py`:** Path on line ~17 uses `os.path.dirname(__file__)` which is fine. But the overall behavior needs to change — instead of committing directly, it should create a branch and open a PR for new entries.

3. **GitHub Actions:** Rewrite workflows for the new repo structure:
   - `validate-pr.yml` — new, runs validation on PRs touching `studios.json`
   - `import-sheet-submissions.yml` — adapted from `sync-studios.yml`, creates PRs instead of direct commits
   - `check-urls.yml` — adapted, fix path

### Deployment pipeline

The ceramics map currently deploys as part of roysclay.co (the whole site deploys together via `gitautodeploy.php` webhook). After the split:

- Option 1: The ceramics-map repo has a deploy Action that SFTPs/rsyncs `index.html`, `studios.json`, and `ma-boundary.geojson` to `roysclay.co/ceramics-map/` on push to `main`.
- Option 2: Use a webhook to trigger `gitautodeploy.php` on the server, pulling from the new repo.
- Option 3: Host on GitHub Pages / Cloudflare Pages and redirect or proxy from roysclay.co.

The `.htaccess` already exists in the ceramics-map directory for CORS. If deploying via SFTP, include it.

### What to do with `roysclayco-website/ceramics-map/`

After the standalone repo is set up and deploying:

1. Delete the `ceramics-map/` directory from `roysclayco-website`
2. Delete the two GitHub Actions workflows (`sync-studios.yml`, `check-studio-urls.yml`)
3. Keep the footer link in `index.html` pointing to `/ceramics-map/`
4. Keep the `sitemap.xml` entry for `/ceramics-map/`
5. Make sure the deploy target directory on the server isn't wiped when roysclayco-website deploys (it's a separate directory, should be fine)

---

## Risk: Data loss during migration

The 170-studio `studios.json` in `roysclayco-website/ceramics-map/` is the most valuable artifact. The standalone repo only has 18 studios. During migration:

1. Copy the 170-studio `studios.json` from roysclayco-website to the standalone repo **first**
2. Verify the count matches
3. Then proceed with everything else

Don't rely on the Google Sheet as backup — `studios.json` is the source of truth after migration.
