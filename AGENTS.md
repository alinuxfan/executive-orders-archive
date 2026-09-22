# AGENTS.md — Agent & Assistant Handbook

This guide is designed for AI coding agents (Antigravity, Cursor, Claude Code, Gemini, Copilot, etc.) working on the **Executive Orders Archive** repository. It outlines architecture principles, invariant constraints, data flows, and verification checklists.

---

## 1. High-Level Architecture

The repository is divided into two distinct subsystems:

```
[Federal Register API / Historical Sources]
                     │
                     ▼
       scripts/sync_orders.py
                     │
                     ▼
  scripts/batch_constitutional_worker.py (NLP / Readability)
                     │
                     ▼
             data/orders.sqlite  <─── (Single Source of Truth)
                     │
     ┌───────────────┴───────────────┐
     ▼                               ▼
scripts/export_site_data.py     scripts/build_search_index.py
     │                               │
     ▼                               ▼
data/site_orders*.json          public/search_index.json
     │                               │
     └───────────────┬───────────────┘
                     ▼
             Astro 5 Frontend (src/)
                     │
                     ▼
            Static Build (dist/) ──> Cloudflare Pages
```

---

## 2. Invariants & Critical Conventions

### Data Pipeline & Database Invariants
1. **Single Source of Truth**: `data/orders.sqlite` is the primary database. Never manually edit `data/site_orders.json` or `data/site_orders_summary.json` directly—always update SQLite and re-export via `scripts/export_site_data.py`.
2. **Protected Enriched Fields (`scripts/db.py`)**:
   - `tone_tag`, `summary_plain_english`, `key_directives_json`, `who_it_affects_json`, and evaluated sentiment metrics are enriched by `batch_constitutional_worker.py`.
   - In `upsert_order()` within [`scripts/db.py`](file:///home/adam/git/executive_orders/scripts/db.py), these fields are protected from accidental overwrite during routine sync fetches using `COALESCE` and `CASE WHEN tone_tag IS NOT NULL`. **Do not bypass this protection.**
3. **Execution Environment for Python**:
   - When running scripts, ensure `PYTHONPATH=scripts` is set so internal module imports (`from db import ...`, `from metrics import ...`) resolve properly:
     ```bash
     PYTHONPATH=scripts python scripts/<script_name>.py
     ```

### Frontend Invariants (Astro 5)
1. **Strict Static Generation**:
   - The site uses `output: 'static'`. Every route is pre-rendered at build time into `dist/`.
   - All `pages/[slug].astro` and `pages/[id].astro` use `getStaticPaths()`.
2. **Canonical URLs & Absolute Links**:
   - `Astro.site` is configured as `https://executiveordersarchive.org`.
   - When generating metadata, OpenGraph tags, RSS feeds, or share links, construct URLs using `new URL(path, Astro.site).toString()`.
3. **Interactive Components (`src/components/`)**:
   - Client scripts in `.astro` files execute on the browser. Always use defensive querying (`container.querySelector(...)`) and check for null elements before attaching listeners.
   - For social sharing ([`ShareButtons.astro`](file:///home/adam/git/executive_orders/src/components/ShareButtons.astro)):
     - Mobile uses the native Web Share API (`navigator.share`) when supported.
     - Desktop copies the link to clipboard, shows visual confirmation, and opens destination sites in new tabs (`window.open(..., '_blank', 'noopener,noreferrer')`).
4. **Bookmarks & Client State**:
   - Bookmarks are managed client-side via `localStorage` in [`public/bookmarks.js`](file:///home/adam/git/executive_orders/dist/bookmarks.js) and displayed in [`src/pages/saved.astro`](file:///home/adam/git/executive_orders/src/pages/saved.astro). Avoid introducing server-side session dependencies.

---

## 3. Key Directory & File Guide

| Path | Purpose |
|---|---|
| [`astro.config.mjs`](file:///home/adam/git/executive_orders/astro.config.mjs) | Astro configuration, Tailwind integration, site URL, and dev server bindings. |
| [`data/orders.sqlite`](file:///home/adam/git/executive_orders/data/orders.sqlite) | SQLite database with complete orders table and indexes. |
| [`data/presidents.json`](file:///home/adam/git/executive_orders/data/presidents.json) | Curated presidential catalog, dates, party, order counts, and slugs. |
| [`data/site_orders.json`](file:///home/adam/git/executive_orders/data/site_orders.json) | Complete orders dataset loaded by Astro at build time. |
| [`data/site_orders_summary.json`](file:///home/adam/git/executive_orders/data/site_orders_summary.json) | Truncated dataset used for index and listing pages to minimize memory footprint. |
| [`scripts/sync_orders.py`](file:///home/adam/git/executive_orders/scripts/sync_orders.py) | Ingests new executive orders from the Federal Register API. |
| [`scripts/constitutional_engine.py`](file:///home/adam/git/executive_orders/scripts/constitutional_engine.py) | Core NLP analyzer for readability, sentiment, and constitutional categorization. |
| [`scripts/batch_constitutional_worker.py`](file:///home/adam/git/executive_orders/scripts/batch_constitutional_worker.py) | Batch runner processing un-enriched records in SQLite. |
| [`scripts/export_site_data.py`](file:///home/adam/git/executive_orders/scripts/export_site_data.py) | Serializes SQLite data into JSON files consumed by Astro. |
| [`scripts/build_search_index.py`](file:///home/adam/git/executive_orders/scripts/build_search_index.py) | Generates `public/search_index.json` for client search. |
| [`src/components/ShareButtons.astro`](file:///home/adam/git/executive_orders/src/components/ShareButtons.astro) | Social share actions (X, Facebook, Instagram, LinkedIn, Copy Link). |
| [`src/components/CitationBox.astro`](file:///home/adam/git/executive_orders/src/components/CitationBox.astro) | Bluebook/legal citation generator. |
| [`src/pages/orders/[id].astro`](file:///home/adam/git/executive_orders/src/pages/orders/[id].astro) | Individual order detail template. |
| [`src/pages/presidents/[slug].astro`](file:///home/adam/git/executive_orders/src/pages/presidents/[slug].astro) | Individual president profile and executive order catalog. |
| [`src/pages/presidents/compare.astro`](file:///home/adam/git/executive_orders/src/pages/presidents/compare.astro) | Side-by-side presidential comparison tool. |
| [`wrangler.jsonc`](file:///home/adam/git/executive_orders/wrangler.jsonc) | Cloudflare Pages deployment configuration pointing to `./dist`. |

---

## 4. Standard Agent Workflows

### Scenario A: Modifying Frontend UI or Components
1. Edit files under `src/components/`, `src/pages/`, or `src/layouts/`.
2. Always test the build before concluding:
   ```bash
   npm run build
   ```
3. Inspect `git diff` to ensure no unexpected generated artifacts or formatting drifts occurred.

### Scenario B: Adding or Updating Data Analysis Fields
1. If adding a new column to SQLite:
   - Update `init_db()` and `fields` array in [`scripts/db.py`](file:///home/adam/git/executive_orders/scripts/db.py).
   - If the field is enriched post-ingestion, add it to `protected_null_coalesce_fields`.
2. Update analysis code in [`scripts/constitutional_engine.py`](file:///home/adam/git/executive_orders/scripts/constitutional_engine.py) or [`scripts/batch_constitutional_worker.py`](file:///home/adam/git/executive_orders/scripts/batch_constitutional_worker.py).
3. Update [`scripts/export_site_data.py`](file:///home/adam/git/executive_orders/scripts/export_site_data.py) so the new field is passed to `site_orders.json` or `site_orders_summary.json`.
4. Re-export data and build search index:
   ```bash
   PYTHONPATH=scripts python scripts/export_site_data.py
   PYTHONPATH=scripts python scripts/build_search_index.py
   npm run build
   ```

---

## 5. Verification Checklist for Agents

Before completing any task or opening a pull request:
- [ ] **Static Build**: `npm run build` completes with exit code 0.
- [ ] **No Dead Links / Missing Slugs**: Dynamic routes in `src/pages/` properly receive required parameters from `site_orders.json` or `presidents.json`.
- [ ] **Dark Mode Compatibility**: Any newly added UI elements include corresponding `dark:` Tailwind variant classes.
- [ ] **Mobile Responsiveness**: UI adapts gracefully to mobile widths (e.g. tooltips positioned properly, button rows wrap cleanly).
- [ ] **Git Cleanliness**: Run `git status` to ensure temp logs (`*.log`), scratch files, or unwanted build outputs aren't mistakenly staged.
