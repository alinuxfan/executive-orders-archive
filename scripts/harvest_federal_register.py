import sys
from pathlib import Path
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
import argparse
import json
import time
from pathlib import Path
import requests
from tqdm import tqdm

from db import init_db, upsert_order, get_connection
from metrics import clean_text_from_html, compute_metrics

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "federal_register"
RAW_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def get_existing_ids():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM orders WHERE source = 'federal_register' AND word_count > 0")
    ids = {row[0] for row in cursor.fetchall()}
    conn.close()
    return ids

def fetch_body_text(doc):
    body_url = doc.get("body_html_url")
    if body_url:
        try:
            resp = requests.get(body_url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                return clean_text_from_html(resp.text)
        except Exception as e:
            print(f"Warning: could not fetch body_html_url for {doc.get('document_number')}: {e}")

    # Fallback to abstract if body_html_url is not available
    return doc.get("abstract") or ""

def harvest_federal_register(limit=None, force=False):
    init_db()
    existing_ids = set() if force else get_existing_ids()
    print(f"Found {len(existing_ids)} existing Federal Register orders in database.")

    base_url = "https://www.federalregister.gov/api/v1/documents.json"
    fields = [
        "document_number", "title", "executive_order_number",
        "signing_date", "publication_date", "president",
        "body_html_url", "html_url", "pdf_url"
    ]
    
    params = {
        "conditions[type][]": "PRESDOCU",
        "conditions[presidential_document_type][]": "executive_order",
        "order": "newest",
        "per_page": 50,
        "fields[]": fields
    }

    url = base_url
    processed_count = 0
    total_docs = None

    pbar = tqdm(desc="Harvesting Federal Register EOs", unit="order")

    while url:
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"Error fetching page {url}: {e}")
            break

        if total_docs is None:
            total_docs = data.get("count", 0)
            pbar.total = min(limit, total_docs) if limit else total_docs
            print(f"Total Federal Register executive orders available: {total_docs}")

        results = data.get("results", [])
        if not results:
            break

        for item in results:
            doc_num = item.get("document_number")
            order_id = f"fr-{doc_num}"

            if not force and order_id in existing_ids:
                pbar.update(1)
                continue

            # Fetch full details and body
            full_text = fetch_body_text(item)
            metrics = compute_metrics(full_text)

            president_data = item.get("president") or {}
            president_name = president_data.get("name") or "Unknown"
            president_slug = president_data.get("identifier")

            eo_num = item.get("executive_order_number")

            order_record = {
                "id": order_id,
                "eo_number": int(eo_num) if eo_num else None,
                "title": item.get("title") or "Untitled Executive Order",
                "president_name": president_name,
                "president_slug": president_slug,
                "signing_date": item.get("signing_date"),
                "publication_date": item.get("publication_date"),
                "source": "federal_register",
                "source_url": item.get("html_url"),
                "pdf_url": item.get("pdf_url"),
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
                "raw_metadata_json": json.dumps(item)
            }

            upsert_order(order_record)
            existing_ids.add(order_id)
            processed_count += 1
            pbar.update(1)

            if limit and processed_count >= limit:
                print(f"\nReached specified limit of {limit} orders.")
                pbar.close()
                return

            time.sleep(0.1)

        url = data.get("next_page_url")
        params = {} # Query params are baked into next_page_url

    pbar.close()
    print(f"\nCompleted harvesting. Total processed this session: {processed_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Harvest Executive Orders from Federal Register API")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of orders to fetch")
    parser.add_argument("--force", action="store_true", help="Force re-fetching existing records")
    args = parser.parse_args()

    harvest_federal_register(limit=args.limit, force=args.force)
