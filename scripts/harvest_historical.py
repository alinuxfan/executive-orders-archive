import sys
from pathlib import Path
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
import argparse
import datetime
import json
import re
import time
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from db import init_db, upsert_order, get_connection
from metrics import clean_text_from_html, compute_metrics

CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "historical"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://www.presidency.ucsb.edu"
CATEGORY_URL = f"{BASE_URL}/documents/app-categories/written-presidential-orders/presidential/executive-orders"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def get_existing_ids():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM orders WHERE source = 'presidency_project' AND word_count > 0")
    ids = {row[0] for row in cursor.fetchall()}
    conn.close()
    return ids

def parse_date(date_str):
    if not date_str:
        return None
    try:
        # e.g. "September 16, 2026" or "July 11, 1826"
        dt = datetime.datetime.strptime(date_str.strip(), "%B %d, %Y")
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return None

def extract_eo_number_from_title(title):
    match = re.search(r"Executive Order\s+(\d+)", title, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

def slugify(text):
    text = text.lower().strip()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")

def fetch_document_content(relative_url):
    slug = relative_url.strip("/").split("/")[-1]
    cache_path = CACHE_DIR / f"{slug}.html"

    if cache_path.exists():
        with open(cache_path, "r", encoding="utf-8") as f:
            html = f.read()
    else:
        url = f"{BASE_URL}{relative_url}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                return "", ""
            html = resp.text
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(html)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return "", ""

    soup = BeautifulSoup(html, "html.parser")
    
    # Extract President name
    author_div = soup.find("div", class_="field-docs-person")
    president_name = "Unknown"
    if author_div:
        pres_a = author_div.find("a")
        if pres_a:
            president_name = pres_a.get_text().strip()
        else:
            first_line = author_div.get_text().strip().split("\n")[0]
            if first_line:
                president_name = first_line.strip()

    # Extract Body content
    body_div = soup.find("div", class_="field-docs-content") or soup.find("div", class_="node-content")
    clean_text = clean_text_from_html(str(body_div)) if body_div else ""

    return president_name, clean_text

def harvest_historical_page(page_num, existing_ids, force=False):
    params = {
        "items_per_page": 100,
        "page": page_num
    }
    try:
        resp = requests.get(CATEGORY_URL, params=params, headers=HEADERS, timeout=20)
        if resp.status_code != 200:
            return 0, 0
    except Exception as e:
        print(f"Error loading page {page_num}: {e}")
        return 0, 0

    soup = BeautifulSoup(resp.text, "html.parser")
    rows = soup.find_all("div", class_="views-row")
    if not rows:
        return 0, 0

    processed = 0
    for row in rows:
        a_tag = row.find("a", href=True)
        if not a_tag:
            continue

        relative_url = a_tag["href"]
        slug = relative_url.strip("/").split("/")[-1]
        order_id = f"app-{slug}"

        if not force and order_id in existing_ids:
            continue

        title = a_tag.get_text().strip()
        date_span = row.find("span", class_="date-display-single")
        signing_date = parse_date(date_span.get_text()) if date_span else None

        president_name, full_text = fetch_document_content(relative_url)
        metrics = compute_metrics(full_text)
        eo_num = extract_eo_number_from_title(title)

        record = {
            "id": order_id,
            "eo_number": eo_num,
            "title": title,
            "president_name": president_name,
            "president_slug": slugify(president_name),
            "signing_date": signing_date,
            "publication_date": None,
            "source": "presidency_project",
            "source_url": f"{BASE_URL}{relative_url}",
            "pdf_url": None,
            "full_text": full_text,
            "word_count": metrics["word_count"],
            "char_count": metrics["char_count"],
            "reading_time_minutes": metrics["reading_time_minutes"],
            "flesch_kincaid_grade": metrics["flesch_kincaid_grade"],
            "sentiment_compound": metrics["sentiment_compound"],
            "sentiment_pos": metrics["sentiment_pos"],
            "sentiment_neg": metrics["sentiment_neg"],
            "sentiment_neu": metrics["sentiment_neu"],
            "sentiment_valence": metrics["sentiment_valence"],
            "summary_plain_english": None,
            "key_directives_json": None,
            "who_it_affects_json": None,
            "tone_tag": None,
            "raw_metadata_json": json.dumps({"title": title, "url": relative_url, "date": signing_date})
        }

        upsert_order(record)
        existing_ids.add(order_id)
        processed += 1
        time.sleep(0.05)

    return len(rows), processed

def harvest_historical(start_page=0, max_pages=None, limit=None, force=False):
    init_db()
    existing_ids = set() if force else get_existing_ids()
    print(f"Found {len(existing_ids)} existing historical orders in database.")

    page = start_page
    total_processed = 0

    pbar = tqdm(desc="Harvesting Historical EOs", unit="order")

    while True:
        if max_pages and (page - start_page) >= max_pages:
            break

        count_in_page, processed = harvest_historical_page(page, existing_ids, force=force)
        if count_in_page == 0:
            print(f"No more items found at page {page}. Ingestion complete.")
            break

        total_processed += processed
        pbar.update(processed)

        if limit and total_processed >= limit:
            print(f"Reached limit of {limit} orders.")
            break

        page += 1
        time.sleep(0.2)

    pbar.close()
    print(f"Historical harvest complete. Total orders processed: {total_processed}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Harvest Historical Executive Orders from UCSB APP")
    parser.add_argument("--start-page", type=int, default=0, help="Starting page number")
    parser.add_argument("--max-pages", type=int, default=None, help="Maximum number of pages to crawl")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of orders to ingest")
    parser.add_argument("--force", action="store_true", help="Force re-fetching existing records")
    args = parser.parse_args()

    harvest_historical(start_page=args.start_page, max_pages=args.max_pages, limit=args.limit, force=args.force)
