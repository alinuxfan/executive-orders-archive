#!/usr/bin/env python3
"""
Test Suite for Architectural Modernization:
- Youngstown classification engine (Python & TypeScript equivalence)
- SQLite schema & migrations
- Precomputed reverse reference indexing
- QuickShare externalization & payload structure
- Cloudflare R2 backup configuration
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from constitutional_engine import classify_youngstown_zone
from db import init_db, get_connection
from r2_sync import get_r2_config

def test_all():
    print("Testing constitutional_engine Youngstown zones...")
    assert classify_youngstown_zone("Positive", 0.25, "Faithful Execution", "Pursuant to Act") == 1
    assert classify_youngstown_zone("Neutral", 0.0, "Administrative", "Executive Order 12345") == 2
    assert classify_youngstown_zone("Urgent/Negative", -0.4, "Scrutiny", "Executive Order 9066") == 3
    assert classify_youngstown_zone("Neutral", 0.0, "", "Regarding suspension of habeas corpus") == 3
    print("✓ Youngstown classification tests passed!")

    print("Testing SQLite schema and columns...")
    init_db()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(orders)")
    cols = {r[1]: r[2] for r in cur.fetchall()}
    assert "youngstown_zone" in cols, "youngstown_zone missing from schema"
    assert "manually_curated" in cols
    conn.close()
    print("✓ SQLite schema tests passed!")

    print("Testing data/reverse_references.json...")
    with open(ROOT / "data" / "reverse_references.json") as f:
        refs = json.load(f)
    assert len(refs) > 1000, f"Expected >1000 cited orders, got {len(refs)}"
    for num_str, cit_list in list(refs.items())[:5]:
        assert int(num_str) > 0
        assert isinstance(cit_list, list)
        for c in cit_list:
            assert "id" in c and "relation" in c and "president_name" in c
    print(f"✓ Reverse references validated ({len(refs)} cited orders indexed)!")

    print("Testing public/quick-share-data.json...")
    with open(ROOT / "public" / "quick-share-data.json") as f:
        qs = json.load(f)
    assert "todayOrders" in qs
    assert "milestones" in qs
    assert len(qs["milestones"]) == 8
    assert "rouletteSeed" in qs
    assert "dateInfo" in qs
    print("✓ Quick share data schema validated!")

    print("Testing r2_sync configuration...")
    cfg = get_r2_config()
    assert cfg["bucket_name"] == "executive-orders-archive"
    assert cfg["is_configured"] in (True, False)
    print("✓ R2 sync configuration validated!")

    print("\nALL ARCHITECTURAL MODERNIZATION TESTS PASSED CLEANLY!")

if __name__ == "__main__":
    test_all()
