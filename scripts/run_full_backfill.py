import argparse
import concurrent.futures
import datetime
import json
import logging
import os
import re
import sys
import threading
import time
import traceback
from pathlib import Path
import requests
from bs4 import BeautifulSoup

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from db import init_db, upsert_order, get_connection
from metrics import clean_text_from_html, compute_metrics
from constitutional_engine import analyze_constitutional_sentiment, generate_statesman_summary
from sync_orders import export_stats_json
from export_site_data import export_all

ROOT_DIR = SCRIPTS_DIR.parent
DATA_DIR = ROOT_DIR / "data"
RAW_HIST_DIR = DATA_DIR / "raw" / "historical"
RAW_HIST_DIR.mkdir(parents=True, exist_ok=True)

PROGRESS_FILE = DATA_DIR / "backfill_progress.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(DATA_DIR / "backfill.log", mode="a", encoding="utf-8")
    ]
)

HEADERS_HTML = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

BASE_UCSB = "https://www.presidency.ucsb.edu"
CAT_URL = f"{BASE_UCSB}/documents/app-categories/written-presidential-orders/presidential/executive-orders"

thread_local = threading.local()

def get_thread_session():
    if not hasattr(thread_local, "session"):
        s = requests.Session()
        s.headers.update(HEADERS_HTML)
        thread_local.session = s
    return thread_local.session

def slugify(text):
    text = (text or "").lower().strip()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")

def parse_date(date_str):
    if not date_str:
        return None
    try:
        dt = datetime.datetime.strptime(date_str.strip(), "%B %d, %Y")
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return None

def extract_eo_number(title):
    m = re.search(r"Executive Order\s+(\d+)", title or "", re.IGNORECASE)
    return int(m.group(1)) if m else None

def update_progress(status, phase, processed, current_page=None, total_pages=109, total_target=10900):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM orders")
        current_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM orders WHERE source = 'presidency_project'")
        app_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM orders WHERE source = 'federal_register'")
        fr_count = cursor.fetchone()[0]
        conn.close()

        progress = {
            "status": status,
            "phase": phase,
            "orders_in_database": current_count,
            "presidency_project_count": app_count,
            "federal_register_count": fr_count,
            "processed_this_session": processed,
            "current_page": current_page,
            "total_pages": total_pages,
            "estimated_target": total_target,
            "percent_complete": min(100.0, round((current_count / total_target) * 100, 1)),
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(progress, f, indent=2)
    except Exception as e:
        logging.warning(f"Error updating progress: {e}")

def fetch_ucsb_doc_safe(item_meta):
    rel_url = item_meta["relative_url"]
    slug = rel_url.strip("/").split("/")[-1]
    cache_file = RAW_HIST_DIR / f"{slug}.html"

    html = ""
    if cache_file.exists() and cache_file.stat().st_size > 300:
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                html = f.read()
        except Exception:
            pass

    if not html:
        url = f"{BASE_UCSB}{rel_url}"
        s = get_thread_session()
        for attempt in range(3):
            try:
                resp = s.get(url, timeout=15)
                if resp.status_code == 200:
                    html = resp.text
                    with open(cache_file, "w", encoding="utf-8") as f:
                        f.write(html)
                    break
            except Exception:
                time.sleep(0.5 + attempt)

    if not html:
        item_meta["president_name"] = "Unknown"
        item_meta["full_text"] = ""
        return item_meta

    soup = BeautifulSoup(html, "html.parser")
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

    body_div = soup.find("div", class_="field-docs-content") or soup.find("div", class_="node-content")
    clean_text = clean_text_from_html(str(body_div)) if body_div else ""
    item_meta["president_name"] = president_name
    item_meta["full_text"] = clean_text
    return item_meta

def run_backfill(start_page=33, max_pages=109):
    logging.info("=================================================================")
    logging.info(f"Starting Comprehensive Executive Orders Archive Backfill (Pages {start_page}-{max_pages})")
    logging.info("Constitutional Analysis & Statesman Summarization: ENABLED")
    logging.info("=================================================================")
    
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM orders WHERE word_count > 0")
    existing_ids = {row[0] for row in cursor.fetchall()}
    cursor.execute("SELECT eo_number FROM orders WHERE eo_number IS NOT NULL AND source = 'federal_register'")
    existing_fr_eos = {row[0] for row in cursor.fetchall()}
    conn.close()

    logging.info(f"Loaded {len(existing_ids)} existing orders with full text, {len(existing_fr_eos)} authoritative Federal Register EOs.")
    update_progress("running", f"page_{start_page}", 0, current_page=start_page, total_pages=max_pages)

    session = requests.Session()
    session.headers.update(HEADERS_HTML)

    total_processed = 0

    for page in range(start_page, max_pages):
        params = {"items_per_page": 100, "page": page}
        resp = None
        for attempt in range(3):
            try:
                resp = session.get(CAT_URL, params=params, timeout=25)
                if resp.status_code == 200:
                    break
            except Exception as e:
                logging.warning(f"Error fetching page {page} attempt {attempt+1}: {e}")
                time.sleep(1 + attempt)

        if not resp or resp.status_code != 200:
            logging.error(f"Failed to load category page {page}, skipping.")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        rows = soup.find_all("div", class_="views-row")
        if not rows:
            logging.info(f"End of archive reached at page {page}.")
            break

        to_fetch = []
        for row in rows:
            a_tag = row.find("a", href=True)
            if not a_tag:
                continue
            rel_url = a_tag["href"]
            slug = rel_url.strip("/").split("/")[-1]
            order_id = f"app-{slug}"

            if order_id in existing_ids:
                continue

            title = a_tag.get_text().strip()
            eo_num = extract_eo_number(title)
            
            # Deduplication guard: skip historical duplicate if Federal Register is already authoritative for this EO
            if eo_num and eo_num in existing_fr_eos:
                continue

            date_span = row.find("span", class_="date-display-single")
            signing_date = parse_date(date_span.get_text()) if date_span else None

            to_fetch.append({
                "id": order_id,
                "relative_url": rel_url,
                "title": title,
                "eo_number": eo_num,
                "signing_date": signing_date
            })

        if to_fetch:
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                results = list(executor.map(fetch_ucsb_doc_safe, to_fetch))

            for item in results:
                try:
                    full_text = item.get("full_text", "")
                    metrics = compute_metrics(full_text)
                    pres_name = item.get("president_name", "Unknown")
                    title = item.get("title", "")
                    w_count = metrics["word_count"]
                    s_date = item.get("signing_date") or ""

                    # Constitutional Statesman Sentiment & Directives
                    const_metrics = analyze_constitutional_sentiment(full_text, title)
                    summary_data = generate_statesman_summary(
                        title=title,
                        president_name=pres_name,
                        signing_date=s_date,
                        full_text=full_text,
                        word_count=w_count,
                        metrics=const_metrics
                    )

                    record = {
                        "id": item["id"],
                        "eo_number": item["eo_number"],
                        "title": title,
                        "president_name": pres_name,
                        "president_slug": slugify(pres_name),
                        "signing_date": s_date or None,
                        "publication_date": None,
                        "source": "presidency_project",
                        "source_url": f"{BASE_UCSB}{item['relative_url']}",
                        "pdf_url": None,
                        "full_text": full_text,
                        "word_count": w_count,
                        "char_count": metrics["char_count"],
                        "reading_time_minutes": metrics["reading_time_minutes"],
                        "flesch_kincaid_grade": metrics["flesch_kincaid_grade"],
                        "sentiment_compound": const_metrics["sentiment_compound"],
                        "sentiment_pos": const_metrics["sentiment_pos"],
                        "sentiment_neg": const_metrics["sentiment_neg"],
                        "sentiment_neu": const_metrics["sentiment_neu"],
                        "sentiment_valence": const_metrics["sentiment_valence"],
                        "summary_plain_english": summary_data["summary_plain_english"],
                        "key_directives_json": json.dumps(summary_data["key_directives"]),
                        "who_it_affects_json": json.dumps(summary_data["who_it_affects"]),
                        "tone_tag": const_metrics["tone_tag"],
                        "raw_metadata_json": json.dumps({"title": title, "url": item["relative_url"], "date": s_date})
                    }

                    upsert_order(record)
                    existing_ids.add(item["id"])
                    total_processed += 1
                except Exception as e:
                    logging.error(f"Error enriching record {item['id']}: {e}\n{traceback.format_exc()}")

        logging.info(f"Page {page}/{max_pages} complete. Processed {len(to_fetch)} new orders (Total this run: {total_processed}).")
        update_progress("running", f"page_{page}", total_processed, current_page=page, total_pages=max_pages)
        time.sleep(0.5)

    update_progress("completed", "complete", total_processed, current_page=max_pages, total_pages=max_pages)
    logging.info(f"Backfill finished! Total new orders processed: {total_processed}")
    
    # Export stats and site data after backfill
    logging.info("Exporting stats and site datasets...")
    export_stats_json()
    export_all()
    logging.info("Site datasets refreshed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Full Executive Orders Backfill (Pages 33-109)")
    parser.add_argument("--start-page", type=int, default=33, help="Start page (default 33)")
    parser.add_argument("--max-pages", type=int, default=109, help="Max pages (default 109)")
    args = parser.parse_args()

    run_backfill(start_page=args.start_page, max_pages=args.max_pages)
