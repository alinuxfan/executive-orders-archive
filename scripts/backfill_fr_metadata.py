"""Backfills Federal Register citation ("59 FR 2935") and disposition notes
("Revoked by: EO 13062, September 29, 1997") onto orders already in the
database. New orders get both fields from sync_orders.py directly; this only
needs re-running if the columns are ever wiped or to refresh dispositions of
older orders that fall outside the sync's 30-day lookback window (e.g. an
order from 2019 that gets revoked today).

    PYTHONPATH=scripts python scripts/backfill_fr_metadata.py
"""
import sys
from pathlib import Path
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from db import init_db, get_connection
from sync_orders import fetch_fr_executive_orders, normalize_eo_notes


def backfill():
    init_db()
    results = fetch_fr_executive_orders(
        fields=["document_number", "executive_order_number", "citation", "executive_order_notes"]
    )
    print(f"Fetched {len(results)} executive orders from the Federal Register.")

    conn = get_connection()
    cursor = conn.cursor()
    matched = 0
    for item in results:
        citation = item.get("citation")
        notes = normalize_eo_notes(item.get("executive_order_notes"))
        cursor.execute(
            "UPDATE orders SET fr_citation = ?, eo_notes = ? WHERE id = ?",
            (citation, notes, f"fr-{item.get('document_number')}"),
        )
        if cursor.rowcount == 0 and item.get("executive_order_number"):
            # Same order ingested from the American Presidency Project instead.
            cursor.execute(
                "UPDATE orders SET fr_citation = ?, eo_notes = ? WHERE eo_number = ? AND title NOT LIKE '%-A—%'",
                (citation, notes, int(item["executive_order_number"])),
            )
        matched += 1 if cursor.rowcount else 0
    conn.commit()
    conn.close()
    print(f"Updated citation/disposition notes on {matched} orders.")


if __name__ == "__main__":
    backfill()
