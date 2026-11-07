# Executive Orders Archive

A comprehensive, searchable historical archive and constitutional analytical engine for United States Executive Orders, from George Washington to the present day.

The platform pairs an automated Python data harvesting, NLP analysis, and Cloudflare R2 backup pipeline with a statically generated [Astro 5](https://astro.build/) frontend deployed on Cloudflare Workers Static Assets.

- **Production URL**: [executiveordersarchive.org](https://executiveordersarchive.org)
- **Cloudflare Workers Deployment**: [executive-orders-archive.agjennings.workers.dev](https://executive-orders-archive.agjennings.workers.dev)

---

## Architecture Overview

```
                                  [ Federal Register API ]
                                             │
                                             ▼
                                  scripts/sync_orders.py
                                             │
                                             ▼
                            scripts/batch_constitutional_worker.py
                               (VADER Sentiment, Readability,
                            Youngstown Framework Classification)
                                             │
                                             ▼
 [ Cloudflare R2 Storage ] ◄───►   data/orders.sqlite  (Single Source of Truth)
   (Zero-Egress Backups via                  │
      scripts/r2_sync.py)                    │
                     ┌───────────────────────┴───────────────────────┐
                     ▼                                               ▼
         scripts/export_site_data.py                    scripts/build_search_index.py
                     │                                               │
         ┌───────────┼───────────────────────────┐                   │
         ▼           ▼                           ▼                   ▼
    data/site_   data/reverse_            public/quick-share-   public/search_index.json
    orders*.json references.json              data.json         public/search_keywords.json
         │       (Top 8 citations/order)   (41 KB on-demand)    (Precomputed Zone 1/2/3)
         │           │                           │                   │
         └───────────┼───────────────────────────┘                   │
                     ▼                                               ▼
              Astro 5 SSG (src/) ────────────────────────► Client Browser
           (10,916 Pre-rendered Pages)                 (Fast Search, Modals, Caching)
                     │
                     ▼
             dist/ Static Bundle
                     │
                     ▼
       Cloudflare Workers Static Assets (wrangler.jsonc)
```

### Core Architecture Highlights

1. **Youngstown Jackson Three-Tier Precomputation**:
   - Executive authority is classified under the *Youngstown Sheet & Tube Co. v. Sawyer (1952)* framework:
     - **Zone 1 (Maximum Authority)**: Orders backed by express or implied statutory or constitutional authorization.
     - **Zone 2 (Twilight Zone)**: Orders issued where Congress is silent or concurrent authority exists.
     - **Zone 3 (Lowest Ebb)**: Orders conflicting with express or implied congressional will or constitutional constraints.
   - Classification is precomputed in Python ([`scripts/constitutional_engine.py`](scripts/constitutional_engine.py)), stored in the SQLite database ([`data/orders.sqlite`](data/orders.sqlite)), and indexed directly into the search index. The frontend and client search perform $O(1)$ fast-path lookups without runtime recalculation.

2. **Decoupled Reverse Citation Index**:
   - Citations and cross-references between all 10,850+ executive orders are extracted via Python in `scripts/export_site_data.py` into a standalone index ([`data/reverse_references.json`](data/reverse_references.json), 2.3 MB).
   - Detail pages ([`src/pages/orders/[id].astro`](src/pages/orders/[id].astro)) and related order lookups no longer import the 65 MB full-dataset JSON into the Astro build graph, reducing V8 heap allocation and accelerating static builds.

3. **Externalized Client Payloads (~470 MB HTML Savings)**:
   - High-cardinality components like [`QuickShareModal.astro`](src/components/QuickShareModal.astro) (supporting "This Day in History", historical milestones, and roulette discovery) load their dynamic datasets on-demand from [`public/quick-share-data.json`](public/quick-share-data.json) (41 KB) via [`public/quick-share.js`](public/quick-share.js).
   - Eliminates ~43 KB of duplicate inlined JSON and script blocks across all 10,916 static HTML pages.

4. **Zero-Egress SQLite Backups via Cloudflare R2**:
   - [`scripts/r2_sync.py`](scripts/r2_sync.py) provides S3-compatible snapshotting and restoration for `data/orders.sqlite` using Cloudflare R2's 10 GB free tier with zero egress costs.
   - Integrated into the automated GitHub Actions sync workflow with graceful zero-op fallback when credentials are omitted in local development.

5. **Cloudflare Edge Headers & Caching**:
   - [`public/_headers`](public/_headers) configures HTTP cache policies and strict security headers (`X-Frame-Options`, `X-Content-Type-Options`, `Strict-Transport-Security`), caching static JSON datasets (`quick-share-data.json`, `search_index.json`) and scripts at edge nodes.

---

## Features

- **230+ Years of Executive Authority**: Comprehensive catalog spanning George Washington to the present, harvested from the American Presidency Project (APP) and the Federal Register API.
- **Constitutional & Linguistic Intelligence**:
  - Youngstown Three-Tier Framework classification (Zone 1, Zone 2, Zone 3).
  - VADER sentiment analysis (compound, positive, negative, neutral valence).
  - Flesch-Kincaid Grade Level and reading complexity metrics.
  - Plain-English executive summaries, key directives, and affected entity detection.
- **Interactive Visualizations**:
  - Volume timeline charts and presidential comparison matrices powered by Chart.js.
  - Tone & sentiment breakdown charts.
  - "This Day in History" exploration module.
- **Search & Exploration**:
  - Client-side full-text search with instant Youngstown Zone, President, and Disposition filtering.
  - Sub-second keyword index loading ([`public/search-lib.js`](public/search-lib.js)).
- **Legal & Research Utilities**:
  - Bluebook / legal citation generator with one-click copy.
  - Bidirectional reverse citations ("Orders Citing This Order").
  - Client-side bookmarks persisted in browser `localStorage`.
  - Founding Documents viewer (U.S. Constitution, Declaration of Independence, Articles of Confederation, Ratifying Conventions).
  - Social card preview and multi-platform sharing.
  - Full RSS feed (`/feed.xml`) and sitemaps.

---

## Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend Framework** | [Astro 5](https://astro.build/) (`output: 'static'`) |
| **Styling** | [Tailwind CSS 3](https://tailwindcss.com/) with responsive dark mode |
| **Visualizations & Icons** | [Chart.js](https://www.chartjs.org/), [Lucide](https://lucide.dev/) |
| **Data Processing & NLP** | Python 3.11+, `vaderSentiment`, `textstat`, `beautifulsoup4`, `requests` |
| **Object Storage Sync** | Cloudflare R2 / `boto3` (`scripts/r2_sync.py`) |
| **Primary Database** | SQLite (`data/orders.sqlite`) with schema migrations |
| **Edge Hosting & CI/CD** | Cloudflare Workers Static Assets (`wrangler.jsonc`), GitHub Actions |

---

## Quickstart

### Prerequisites
- **Node.js** (v18.17+ or v20+)
- **Python** (3.10+ recommended for data pipeline)

### 1. Frontend Development

```bash
# Install dependencies
npm install

# Start local dev server (http://localhost:4321)
npm run dev

# Run full production static build (compiles 10,900+ pages into dist/)
npm run build

# Preview production build locally
npm run preview
```

### 2. Python Data Pipeline

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python requirements
pip install -r requirements.txt

# Run the architecture test suite
python scripts/test_modernization.py
```

---

## Project Structure

```
.
├── astro.config.mjs             # Astro 5 configuration (site URL, Tailwind, Sitemap, RSS)
├── data/
│   ├── orders.sqlite            # SQLite database (Single source of truth with 10,850+ orders)
│   ├── presidents.json          # Curated presidential catalog, terms, and party affiliations
│   ├── reverse_references.json  # Precomputed reverse citation index (top citations/order)
│   ├── site_orders.json         # Complete orders dataset for detail page generation
│   ├── site_orders_summary.json # Truncated dataset for fast listing views
│   ├── stats.json               # Aggregated platform analytics and sentiment distributions
│   └── founding/                # JSON texts for founding charters and convention debates
├── dist/                        # Compiled static production bundle deployed to Cloudflare
├── public/
│   ├── _headers                 # Cloudflare edge caching and security headers
│   ├── quick-share-data.json    # Externalized date & milestone metadata for discovery modal
│   ├── quick-share.js           # Client controller for the Quick Share modal
│   ├── search-lib.js            # Shared search, filtering, and card rendering library
│   ├── search_index.json        # Precomputed client-side search index with Youngstown zones
│   └── search_keywords.json     # Full-text body keyword index (lazily loaded)
├── scripts/
│   ├── batch_constitutional_worker.py # NLP & Youngstown classification enrichment
│   ├── build_search_index.py    # Generates search_index.json & search_keywords.json
│   ├── constitutional_engine.py # Core NLP, sentiment, and Youngstown classification logic
│   ├── db.py                    # SQLite schema, connection pooling, and migrations
│   ├── export_site_data.py      # Serializes SQLite data into JSON & reverse references
│   ├── r2_sync.py               # Cloudflare R2 backup & restore utility
│   ├── sync_orders.py           # Ingests newly published orders from Federal Register API
│   └── test_modernization.py    # Automated test suite for schema, zones, and exports
├── src/
│   ├── components/              # Reusable Astro UI components (QuickShareModal, Charts, Cards)
│   ├── layouts/                 # Root layout with responsive header, navigation, and footer
│   ├── lib/                     # TypeScript libraries (youngstown.ts, relatedOrders.ts)
│   └── pages/                   # Static page routes (orders/, presidents/, founding/, timeline)
└── wrangler.jsonc               # Cloudflare Workers Static Assets configuration
```

---

## Data Pipeline & Maintenance

The repository runs automated syncs twice every weekday via GitHub Actions ([`.github/workflows/sync-orders.yml`](.github/workflows/sync-orders.yml)).

To run the pipeline locally:

```bash
# 1. Fetch newly published orders from Federal Register API
PYTHONPATH=scripts python scripts/sync_orders.py

# 2. Run NLP enrichment and Youngstown Zone classification
PYTHONPATH=scripts python scripts/batch_constitutional_worker.py

# 3. Export JSON datasets & reverse citations
PYTHONPATH=scripts python scripts/export_site_data.py

# 4. Refresh client-side search indexes
PYTHONPATH=scripts python scripts/build_search_index.py

# 5. Run test suite
python scripts/test_modernization.py

# 6. Rebuild static site
npm run build
```

### Cloudflare R2 Database Backups

The SQLite database can be backed up to Cloudflare R2 for zero-egress disaster recovery:

```bash
# Check status of local vs remote database
python scripts/r2_sync.py status

# Upload local orders.sqlite to R2
python scripts/r2_sync.py upload

# Download latest database snapshot from R2
python scripts/r2_sync.py download
```

*Required environment variables (optional for local dev, supported in GitHub Actions)*:
- `R2_ACCOUNT_ID`
- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`
- `R2_BUCKET_NAME` (defaults to `executive-orders-db`)

---

## Deployment

Deployments are hosted on **Cloudflare Workers Static Assets**:

```bash
# Build production bundle
npm run build

# Deploy directly via Wrangler
npx wrangler deploy
```

- Configuration: [`wrangler.jsonc`](wrangler.jsonc)
- Static output directory: `./dist`
- Assets are deployed to Cloudflare's global edge network.

---

## License

Executive order texts and official United States government publications are in the public domain. Archive source code, analytical pipelines, and site design are licensed under the MIT License.
