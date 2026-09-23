import sys
from pathlib import Path
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
import datetime
import json
import os
import sys
from pathlib import Path
import requests

from db import init_db, upsert_order, get_connection, get_order, log_field_changes
from metrics import clean_text_from_html, compute_metrics

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
SYNC_STATUS_FILE = DATA_DIR / "sync_status.json"

HEADERS = {
    "User-Agent": "ExecutiveOrdersSyncBot/1.0 (Public Open Data Tracker; mailto:info@executiveorders.io)"
}

def get_latest_order_info():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT MAX(signing_date), MAX(publication_date), COUNT(*) 
        FROM orders 
        WHERE source = 'federal_register'
    """)
    latest_signing, latest_pub, total_count = cursor.fetchone()
    conn.close()
    return latest_signing, latest_pub, total_count

def fetch_body_text(body_url):
    if not body_url:
        return ""
    try:
        resp = requests.get(body_url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            return clean_text_from_html(resp.text)
    except Exception as e:
        print(f"Failed to fetch body text from {body_url}: {e}")
    return ""

def export_stats_json():
    conn = get_connection()
    cursor = conn.cursor()

    # Total orders
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]

    # Breakdown by valence
    cursor.execute("SELECT sentiment_valence, COUNT(*) FROM orders GROUP BY sentiment_valence")
    sentiment_breakdown = {row[0]: row[1] for row in cursor.fetchall()}

    # Breakdown by president
    cursor.execute("""
        SELECT president_name, COUNT(*), ROUND(AVG(word_count), 0), ROUND(AVG(sentiment_compound), 3) 
        FROM orders 
        GROUP BY president_name 
        ORDER BY COUNT(*) DESC
    """)
    president_stats = [
        {
            "president": row[0],
            "total_orders": row[1],
            "avg_word_count": row[2],
            "avg_sentiment": row[3]
        }
        for row in cursor.fetchall()
    ]

    # 10 most recent orders
    cursor.execute("""
        SELECT id, eo_number, title, president_name, signing_date, word_count, reading_time_minutes, sentiment_valence, sentiment_compound
        FROM orders 
        ORDER BY signing_date DESC, id DESC 
        LIMIT 10
    """)
    recent_orders = [
        {
            "id": row[0],
            "eo_number": row[1],
            "title": row[2],
            "president_name": row[3],
            "signing_date": row[4],
            "word_count": row[5],
            "reading_time_minutes": row[6],
            "sentiment_valence": row[7],
            "sentiment_compound": row[8]
        }
        for row in cursor.fetchall()
    ]

    conn.close()

    generated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    stats_payload = {
        "generated_at": generated_at,
        # Alias read by the site header banner (Layout.astro), which historically
        # expected this field on stats.json rather than sync_status.json.
        "last_sync_timestamp": generated_at,
        "total_orders": total_orders,
        "sentiment_breakdown": sentiment_breakdown,
        "presidents": president_stats,
        "recent_orders": recent_orders
    }

    with open(DATA_DIR / "stats.json", "w", encoding="utf-8") as f:
        json.dump(stats_payload, f, indent=2)

    print(f"Exported data/stats.json with {total_orders} total orders.")

def sync_orders(days_lookback=30):
    init_db()
    latest_signing, latest_pub, initial_count = get_latest_order_info()
    print(f"Database contains {initial_count} Federal Register orders.")
    print(f"Latest signing date in DB: {latest_signing}, publication date: {latest_pub}")

    # Determine query date cutoff
    if latest_pub:
        try:
            pub_dt = datetime.datetime.strptime(latest_pub, "%Y-%m-%d")
            since_date = (pub_dt - datetime.timedelta(days=days_lookback)).strftime("%Y-%m-%d")
        except Exception:
            since_date = (datetime.datetime.now() - datetime.timedelta(days=days_lookback)).strftime("%Y-%m-%d")
    else:
        since_date = "2024-01-01"

    print(f"Querying Federal Register for executive orders published on or after: {since_date}")

    base_url = "https://www.federalregister.gov/api/v1/documents.json"
    fields = [
        "document_number", "title", "executive_order_number",
        "signing_date", "publication_date", "president",
        "body_html_url", "html_url", "pdf_url"
    ]
    params = {
        "conditions[type][]": "PRESDOCU",
        "conditions[presidential_document_type][]": "executive_order",
        "conditions[publication_date][gte]": since_date,
        "order": "newest",
        "per_page": 50,
        "fields[]": fields
    }

    resp = requests.get(base_url, params=params, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    results = data.get("results", [])
    print(f"Federal Register returned {len(results)} candidate documents in window.")

    new_or_updated = 0
    for item in results:
        doc_num = item.get("document_number")
        order_id = f"fr-{doc_num}"
        body_text = fetch_body_text(item.get("body_html_url"))
        metrics = compute_metrics(body_text)

        president_data = item.get("president") or {}
        eo_num = item.get("executive_order_number")

        record = {
            "id": order_id,
            "eo_number": int(eo_num) if eo_num else None,
            "title": item.get("title") or "Untitled Executive Order",
            "president_name": president_data.get("name") or "Unknown",
            "president_slug": president_data.get("identifier"),
            "signing_date": item.get("signing_date"),
            "publication_date": item.get("publication_date"),
            "source": "federal_register",
            "source_url": item.get("html_url"),
            "pdf_url": item.get("pdf_url"),
            "full_text": body_text,
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

        existing = get_order(order_id)
        upsert_order(record)
        changes = log_field_changes(order_id, existing, record)
        if changes:
            changed_fields = ", ".join(c[1] for c in changes)
            print(f"  Detected changes for {order_id}: {changed_fields}")
        new_or_updated += 1

    # Export stats JSON
    export_stats_json()

    # Record sync status
    status = {
        "last_sync_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "success",
        "orders_checked": len(results),
        "orders_synced": new_or_updated,
        "since_date": since_date
    }
    with open(SYNC_STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2)

    print(f"Sync successfully completed. {new_or_updated} orders synced/updated.")
    return new_or_updated

if __name__ == "__main__":
    sync_orders()
