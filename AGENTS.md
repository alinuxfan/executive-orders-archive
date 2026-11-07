# AGENTS.md — Agent & Assistant Handbook

This guide is designed for AI coding agents (Antigravity, Cursor, Claude Code, Gemini, Copilot, etc.) working on the **Executive Orders Archive** repository. It outlines architecture principles, invariant constraints, data flows, and verification checklists.

---

## 1. High-Level Architecture

The platform integrates an automated Python data harvesting, NLP analysis, and Cloudflare R2 backup pipeline with an Astro 5 static site generation frontend deployed to Cloudflare Workers Static Assets.

```
                    [Federal Register API / Historical Sources]
                                         │
                                         ▼
                               scripts/sync_orders.py
                                         │
                                         ▼
                      scripts/batch_constitutional_worker.py
                       (Sentiment, Readability, Youngstown)
                                         │
                                         ▼
 [Cloudflare R2 Storage] ◄───►   data/orders.sqlite  (Single Source of Truth)
   (Zero-Egress Backups via              │
      scripts/r2_sync.py)                │
                     ┌───────────────────┴───────────────────┐
                     ▼                                       ▼
         scripts/export_site_data.py            scripts/build_search_index.py
                     │                                       │
     ┌───────────────┼──────────────────────┐                │
     ▼               ▼                      ▼                ▼
data/site_      data/reverse_        public/quick-share-  public/search_index.json
orders*.json    references.json          data.json        public/search_keywords.json
(Full & Summary)(Top 8 citations/order) (41 KB on-demand) (Precomputed Zone 1/2/3)
     │               │                      │                │
     └───────────────┼──────────────────────┘                │
                     ▼                                       ▼
             Astro 5 SSG (src/) ────────────────────► Client Browser
          (10,916 Static HTML Pages)                (Search, Modals, Caching)
                     │
                     ▼
             dist/ Static Bundle
                     │
                     ▼
      Cloudflare Workers Static Assets (wrangler.jsonc)
```

---

## 2. Invariants & Critical Conventions

### Data Pipeline & Database Invariants
1. **Single Source of Truth**:
   - `data/orders.sqlite` is the primary database. Never manually edit `data/site_orders.json`, `data/site_orders_summary.json`, or `data/reverse_references.json` directly—always update SQLite and re-export via `scripts/export_site_data.py`.
2. **Protected Enriched Fields (`scripts/db.py`)**:
   - `youngstown_zone`, `tone_tag`, `summary_plain_english`, `key_directives_json`, `who_it_affects_json`, and sentiment metrics are enriched by `batch_constitutional_worker.py`.
   - In `upsert_order()` within [`scripts/db.py`](file:///home/adam/git/executive_orders/scripts/db.py), these fields are protected from accidental overwrite during routine sync fetches using `COALESCE` and `CASE WHEN ... IS NOT NULL`. **Do not bypass this protection.**
3. **Youngstown Jackson Three-Tier Framework**:
   - `youngstown_zone` (INTEGER: `1` for Maximum Authority, `2` for Twilight Zone, `3` for Lowest Ebb) must be computed in Python via `classify_youngstown_zone()` in [`scripts/constitutional_engine.py`](file:///home/adam/git/executive_orders/scripts/constitutional_engine.py).
   - Stored directly in `orders.sqlite` and exported into `search_index.json`. Client and Astro templates must use the precomputed integer for $O(1)$ fast paths rather than re-evaluating regex or sentiment heuristics at render time.
4. **Decoupled Reverse Citations (`data/reverse_references.json`)**:
   - Reverse legal citations ("Orders Citing This Order") are precomputed by [`scripts/export_site_data.py`](file:///home/adam/git/executive_orders/scripts/export_site_data.py) into `data/reverse_references.json`.
   - **CRITICAL**: Never import `data/site_orders.json` (65+ MB) into [`src/lib/relatedOrders.ts`](file:///home/adam/git/executive_orders/src/lib/relatedOrders.ts) or any individual page component. Doing so causes V8 heap memory exhaustion during Astro's multi-thousand-page static build.
5. **Hand-curated and LLM summaries**:
   - Orders with `manually_curated = 1` or a non-null `summary_model` are skipped by `batch_constitutional_worker.py`, even with `--force`.
   - To hand-edit an order's summary, update SQLite and set `manually_curated = 1` — edits made directly to `site_orders.json` will be wiped by the next export.
6. **Execution Environment for Python**:
   - When running scripts, ensure `PYTHONPATH=scripts` is set so internal module imports (`from db import ...`, `from metrics import ...`) resolve properly:
     ```bash
     PYTHONPATH=scripts python scripts/<script_name>.py
     ```

### Frontend Invariants (Astro 5)
1. **Strict Static Generation (`output: 'static'`)**:
   - Every route is pre-rendered at build time into `dist/`.
   - All `pages/[slug].astro` and `pages/[id].astro` use `getStaticPaths()`.
2. **Eliminate Layout Inlining Bloat**:
   - Never embed large JSON payloads (such as thousands of historical dates or search catalogs) inline via `<script set:html={JSON.stringify(...)}>` inside components rendered on every page (like `Layout.astro` or `QuickShareModal.astro`).
   - Across 10,900+ pages, every 40 KB inlined multiplies to ~450 MB of duplicated HTML.
   - Always externalize shared data into `public/*.json` and fetch it asynchronously on demand via client-side JavaScript.
3. **Canonical URLs & Absolute Links**:
   - `Astro.site` is configured as `https://executiveordersarchive.org`.
   - When generating metadata, OpenGraph tags, RSS feeds, or share links, construct URLs using `new URL(path, Astro.site).toString()`.
4. **Interactive Components (`src/components/`)**:
   - Client scripts in `.astro` files execute on the browser. Always use defensive querying (`container.querySelector(...)`) and check for null elements before attaching listeners.
   - Mobile uses the native Web Share API (`navigator.share`) when supported; desktop copies the link to clipboard and provides visual feedback.
5. **Bookmarks & Client State**:
   - Bookmarks are managed client-side via `localStorage` in [`public/bookmarks.js`](file:///home/adam/git/executive_orders/dist/bookmarks.js) and displayed in [`src/pages/saved.astro`](file:///home/adam/git/executive_orders/src/pages/saved.astro). Avoid introducing server-side session dependencies.

---

## 3. Key Directory & File Guide

| Path | Purpose |
|---|---|
| [`astro.config.mjs`](file:///home/adam/git/executive_orders/astro.config.mjs) | Astro configuration, Tailwind integration, site URL, and sitemap settings. |
| [`data/orders.sqlite`](file:///home/adam/git/executive_orders/data/orders.sqlite) | SQLite database with complete orders table, indexes, and migrations. |
| [`data/presidents.json`](file:///home/adam/git/executive_orders/data/presidents.json) | Curated presidential catalog, dates, party affiliations, order counts, and slugs. |
| [`data/reverse_references.json`](file:///home/adam/git/executive_orders/data/reverse_references.json) | Precomputed reverse citation map (top 8 citations per EO number, 2.3 MB). |
| [`data/site_orders.json`](file:///home/adam/git/executive_orders/data/site_orders.json) | Complete orders dataset for detail page generation. |
| [`data/site_orders_summary.json`](file:///home/adam/git/executive_orders/data/site_orders_summary.json) | Truncated dataset used for index and listing pages to minimize memory footprint. |
| [`public/_headers`](file:///home/adam/git/executive_orders/public/_headers) | Cloudflare edge caching policies and security headers. |
| [`public/quick-share-data.json`](file:///home/adam/git/executive_orders/public/quick-share-data.json) | Externalized dataset for today-in-history, milestones, and roulette (41 KB). |
| [`public/quick-share.js`](file:///home/adam/git/executive_orders/public/quick-share.js) | Client controller for the Quick Share modal. |
| [`public/search-lib.js`](file:///home/adam/git/executive_orders/public/search-lib.js) | Shared client search, filtering, and card template rendering. |
| [`public/search_index.json`](file:///home/adam/git/executive_orders/public/search_index.json) | Precomputed client-side search index with Youngstown zones. |
| [`public/search_keywords.json`](file:///home/adam/git/executive_orders/public/search_keywords.json) | Full-text keywords lazily fetched when search input is focused. |
| [`scripts/batch_constitutional_worker.py`](file:///home/adam/git/executive_orders/scripts/batch_constitutional_worker.py) | Batch runner processing NLP enrichment and Youngstown classification in SQLite. |
| [`scripts/build_search_index.py`](file:///home/adam/git/executive_orders/scripts/build_search_index.py) | Generates `public/search_index.json` and `public/search_keywords.json`. |
| [`scripts/constitutional_engine.py`](file:///home/adam/git/executive_orders/scripts/constitutional_engine.py) | Core NLP analyzer: readability, sentiment, and Youngstown Jackson classification. |
| [`scripts/db.py`](file:///home/adam/git/executive_orders/scripts/db.py) | SQLite schema, connection management, migrations, and protected upserts. |
| [`scripts/export_site_data.py`](file:///home/adam/git/executive_orders/scripts/export_site_data.py) | Exports SQLite records to `site_orders*.json`, `reverse_references.json`, and `quick-share-data.json`. |
| [`scripts/r2_sync.py`](file:///home/adam/git/executive_orders/scripts/r2_sync.py) | Cloudflare R2 backup, restore, and status utility with boto3. |
| [`scripts/sync_orders.py`](file:///home/adam/git/executive_orders/scripts/sync_orders.py) | Ingests newly published executive orders from the Federal Register API. |
| [`scripts/test_modernization.py`](file:///home/adam/git/executive_orders/scripts/test_modernization.py) | Automated test suite validating schema, classification, reverse citations, and R2 config. |
| [`src/components/QuickShareModal.astro`](file:///home/adam/git/executive_orders/src/components/QuickShareModal.astro) | Quick Share modal markup; loads data and JS dynamically. |
| [`src/lib/relatedOrders.ts`](file:///home/adam/git/executive_orders/src/lib/relatedOrders.ts) | Related and cited order resolution using `data/reverse_references.json`. |
| [`src/lib/youngstown.ts`](file:///home/adam/git/executive_orders/src/lib/youngstown.ts) | TypeScript Youngstown utility with $O(1)$ fast-path lookups. |
| [`wrangler.jsonc`](file:///home/adam/git/executive_orders/wrangler.jsonc) | Cloudflare Workers Static Assets deployment configuration pointing to `./dist`. |

---

## 4. Standard Agent Workflows

### Scenario A: Modifying Frontend UI or Components
1. Edit files under `src/components/`, `src/pages/`, or `src/layouts/`.
2. Ensure no large data blobs are inlined into global templates.
3. Test the build before concluding:
   ```bash
   npm run build
   ```
4. Inspect `git diff` to ensure no unexpected generated artifacts or formatting drifts occurred.

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
   python scripts/test_modernization.py
   npm run build
   ```

### Scenario C: Deploying Changes to Production
1. Verify the static build succeeds:
   ```bash
   npm run build
   ```
2. Deploy to Cloudflare Workers Static Assets:
   ```bash
   npx wrangler deploy
   ```

---

## 5. Verification Checklist for Agents

Before completing any task or opening a pull request:
- [ ] **Modernization Tests**: `python scripts/test_modernization.py` passes all checks.
- [ ] **Static Build**: `npm run build` completes with exit code 0.
- [ ] **No Memory Regressions**: `src/lib/relatedOrders.ts` uses `data/reverse_references.json` (do not import `site_orders.json`).
- [ ] **No Inlined HTML Bloat**: Layout components do not inline multi-kilobyte JSON objects; externalized to `public/`.
- [ ] **No Dead Links / Missing Slugs**: Dynamic routes in `src/pages/` properly receive required parameters.
- [ ] **Dark Mode Compatibility**: Any newly added UI elements include corresponding `dark:` Tailwind variant classes.
- [ ] **Mobile Responsiveness**: UI adapts gracefully to mobile widths (e.g. tooltips positioned properly, button rows wrap cleanly).
- [ ] **Git Cleanliness**: Run `git status` to ensure temp logs (`*.log`), scratch files, or unwanted build outputs aren't mistakenly staged.
