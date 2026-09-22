# Executive Orders Archive

A comprehensive, searchable historical archive and analytical engine for United States Executive Orders, from George Washington to the present day.

The platform combines an automated Python data harvesting and constitutional text-analysis pipeline with a fast, statically-generated [Astro 5](https://astro.build/) frontend deployed on Cloudflare Pages.

Live site: [executiveordersarchive.org](https://executiveordersarchive.org)

---

## Features

- **Historical & Modern Coverage**: Spans over 230 years of presidential executive actions, harvested from both the American Presidency Project (APP) and the Federal Register API.
- **Constitutional & Linguistic Intelligence**:
  - Sentiment analysis (compound, positive, negative, neutral) via VADER.
  - Readability and complexity metrics (Flesch-Kincaid Grade Level, word and character counts, estimated reading time).
  - Plain-English summaries, key directives, affected entities, and tone classification.
- **Interactive Visualizations**:
  - Presidential comparison tools and volume timeline charts (powered by Chart.js).
  - Tone & sentiment breakdown charts.
  - "This Day in History" historical discovery module.
- **Founding Documents**: Integrated texts of the Declaration of Independence, Articles of Confederation, U.S. Constitution, Amendments, and Ratifying Convention debates.
- **Research Utilities**:
  - Bluebook / legal citation generator with one-click copy.
  - Client-side bookmarks (saved orders persist locally in browser `localStorage`).
  - Social sharing (X, Facebook, Instagram, LinkedIn, and direct link copy).
  - Full-text search index, RSS feed (`/feed.xml`), and XML sitemaps.

---

## Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend Framework** | [Astro 5](https://astro.build/) (Static Site Generation / `output: 'static'`) |
| **Styling** | [Tailwind CSS 3](https://tailwindcss.com/) with dark mode support |
| **Charts & Icons** | [Chart.js](https://www.chartjs.org/), [Lucide](https://lucide.dev/) |
| **Data Harvesting & NLP** | Python 3.11+, `requests`, `beautifulsoup4`, `vaderSentiment`, `textstat` |
| **Data Storage** | SQLite (`data/orders.sqlite`) exporting to optimized JSON bundles |
| **Hosting & CI/CD** | Cloudflare Pages (`wrangler.jsonc`), GitHub Actions (`.github/workflows/sync-orders.yml`) |

---

## Quickstart

### Prerequisites
- **Node.js** (v18.17+ or v20+)
- **Python** (3.10+ recommended for data scripts)

### 1. Frontend Development

```bash
# Install dependencies
npm install

# Start local development server (runs on http://localhost:4321)
npm run dev

# Build production static bundle (dist/)
npm run build

# Preview production build locally
npm run preview
```

### 2. Python Data Pipeline (Optional for frontend-only edits)

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python requirements
pip install -r requirements.txt
```

---

## Project Structure

```
.
├── astro.config.mjs            # Astro configuration (site URL, Tailwind, Sitemap)
├── data/
│   ├── orders.sqlite           # Primary SQLite database with all raw and processed orders
│   ├── presidents.json         # Structured metadata for all U.S. presidents
│   ├── site_orders.json        # Full JSON dataset bundled for static page generation
│   ├── site_orders_summary.json# Lightweight JSON for listing views & quick lookups
│   ├── stats.json              # Aggregated historical metrics, totals, and distributions
│   └── founding/               # JSON texts for founding documents
├── dist/                       # Static build output (deployed to Cloudflare Pages)
├── public/
│   ├── favicon.svg             # Favicon
│   └── search_index.json       # Precomputed client-side search index
├── scripts/                    # Python pipeline scripts
│   ├── sync_orders.py          # Daily sync fetcher from Federal Register
│   ├── batch_constitutional_worker.py # NLP & constitutional enrichment processor
│   ├── export_site_data.py     # Exports SQLite records to data/site_orders*.json
│   ├── build_search_index.py   # Generates public/search_index.json
│   └── db.py                   # SQLite schema, connection management, and upsert logic
├── src/
│   ├── components/             # Reusable Astro UI components (ShareButtons, Charts, Cards)
│   ├── layouts/                # Base layout with navigation, footer, dark mode toggle
│   ├── lib/                    # Shared TypeScript utilities (portraits, summaries, dates)
│   ├── pages/                  # Static file-based routing
│   │   ├── orders/             # Order catalog and individual order detail pages
│   │   ├── presidents/         # President list, detail, and side-by-side comparison
│   │   ├── founding/           # Founding documents viewer
│   │   ├── analytics.astro     # Platform-wide statistics and charts
│   │   ├── timeline.astro      # Interactive chronological timeline
│   │   └── saved.astro         # LocalStorage bookmarks manager
│   └── styles/
│       └── global.css          # Tailwind base & custom styles
└── wrangler.jsonc              # Cloudflare Pages deployment configuration
```

---

## Data Pipeline & Maintenance

The repository uses automated GitHub Actions (`.github/workflows/sync-orders.yml`) to check for and ingest newly issued executive orders twice every weekday.

To run the data sync manually:

```bash
# 1. Fetch latest orders from Federal Register
PYTHONPATH=scripts python scripts/sync_orders.py

# 2. Enrich unanalyzed orders with readability & tone metrics
PYTHONPATH=scripts python scripts/batch_constitutional_worker.py

# 3. Export static datasets for Astro build
PYTHONPATH=scripts python scripts/export_site_data.py

# 4. Refresh client search index
PYTHONPATH=scripts python scripts/build_search_index.py

# 5. Rebuild static site
npm run build
```

---

## Deployment

Deployments are hosted on **Cloudflare Pages**.

- Static output directory: `./dist`
- Production configuration: [`wrangler.jsonc`](wrangler.jsonc)
- Automatically redeployed when changes are pushed to `main`.

---

## License

Executive order texts and official U.S. government publications are in the public domain. Archive source code and analytical scripts are provided under the MIT License.
