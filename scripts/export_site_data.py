import sys
from pathlib import Path
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
import json
import re
from pathlib import Path
from db import get_connection
from dispositions import build_dispositions
from snippets import operative_snippet

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"

def export_all():
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch all orders
    cursor.execute("""
        SELECT id, eo_number, title, president_name, president_slug, signing_date, publication_date,
               source, source_url, pdf_url, word_count, char_count, reading_time_minutes, flesch_kincaid_grade,
               sentiment_compound, sentiment_pos, sentiment_neg, sentiment_neu, sentiment_valence,
               summary_plain_english, key_directives_json, who_it_affects_json, tone_tag,
               topic_tags_json, fr_citation, eo_notes, full_text
        FROM orders 
        ORDER BY signing_date DESC, id DESC
    """)
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    orders = []
    for r in rows:
        d = dict(zip(columns, r))
        # "Executive Order 11359-A—..." shares eo_number 11359 with the unsuffixed
        # order; the suffix disambiguates display labels and cross-reference links.
        suffix = re.match(r"^Executive Order\s*\d+-([A-Z])\b", d["title"] or "")
        d["eo_suffix"] = suffix.group(1) if suffix else None
        orders.append(d)

    dispositions = build_dispositions(orders)
    for d in orders:
        disposition = dispositions.get(d["id"])
        d["disposition_json"] = json.dumps(disposition, ensure_ascii=False) if disposition else None
        d["eo_status"] = disposition["status"] if disposition else None
        del d["eo_notes"]

    # Compact (no indent, no ASCII-escaping) rather than pretty-printed — these
    # files are machine-generated and only ever read by `import` in Astro, never
    # hand-edited, and indent=2 was measurably ~40% of their on-disk size at this
    # scale (11k+ records). Read data/orders.sqlite directly if you need to
    # inspect field values interactively.
    json_kwargs = {"ensure_ascii": False, "separators": (",", ":")}

    # Write site_orders.json
    with open(DATA_DIR / "site_orders.json", "w", encoding="utf-8") as f:
        json.dump(orders, f, **json_kwargs)

    # Write site_orders_summary.json: listing/index pages only. Fields read solely
    # by the order detail page (which imports site_orders.json) are dropped to
    # keep this file — imported by a dozen pages at build time — small.
    detail_only_fields = {
        "full_text", "summary_plain_english", "key_directives_json", "who_it_affects_json",
        "sentiment_pos", "sentiment_neg", "sentiment_neu", "char_count", "pdf_url",
        "publication_date", "disposition_json",
    }
    summary_orders = []
    for o in orders:
        summary_o = {k: v for k, v in o.items() if k not in detail_only_fields}
        summary_o["snippet"] = operative_snippet(o["full_text"], o["title"], 280)
        summary_orders.append(summary_o)

    with open(DATA_DIR / "site_orders_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_orders, f, **json_kwargs)

    print(f"Exported {len(orders)} orders to data/site_orders.json and data/site_orders_summary.json")
    conn.close()

if __name__ == "__main__":
    export_all()
