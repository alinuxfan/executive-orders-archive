import sys
from pathlib import Path
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
import json
from pathlib import Path
from db import get_connection

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"

def export_all():
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch all orders
    cursor.execute("""
        SELECT id, eo_number, title, president_name, president_slug, signing_date, publication_date, 
               source, source_url, word_count, char_count, reading_time_minutes, flesch_kincaid_grade, 
               sentiment_compound, sentiment_pos, sentiment_neg, sentiment_neu, sentiment_valence,
               summary_plain_english, key_directives_json, who_it_affects_json, tone_tag, full_text
        FROM orders 
        ORDER BY signing_date DESC, id DESC
    """)
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    orders = []
    for r in rows:
        d = dict(zip(columns, r))
        # Keep full_text in individual items
        orders.append(d)

    # Write site_orders.json
    with open(DATA_DIR / "site_orders.json", "w", encoding="utf-8") as f:
        json.dump(orders, f, indent=2)

    # Write site_orders_summary.json (lighter version without huge full_text for index/search)
    summary_orders = []
    for o in orders:
        summary_o = dict(o)
        summary_o["snippet"] = (o["full_text"] or "")[:280] + "..." if o["full_text"] and len(o["full_text"]) > 280 else (o["full_text"] or "")
        del summary_o["full_text"]
        summary_orders.append(summary_o)

    with open(DATA_DIR / "site_orders_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_orders, f, indent=2)

    print(f"Exported {len(orders)} orders to data/site_orders.json and data/site_orders_summary.json")
    conn.close()

if __name__ == "__main__":
    export_all()
