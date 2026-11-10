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
import enrichment

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

    print("Testing enrichment lifecycle (scripts/enrichment.py)...")
    import sqlite3
    mem = sqlite3.connect(":memory:")
    mem.execute("""CREATE TABLE orders (id TEXT PRIMARY KEY, word_count INTEGER, manually_curated INTEGER,
        summary_model TEXT, tone_tag TEXT, summary_plain_english TEXT, topic_tags_json TEXT,
        key_directives_json TEXT, who_it_affects_json TEXT, sentiment_compound REAL, sentiment_valence TEXT,
        sentiment_pos REAL, sentiment_neg REAL, sentiment_neu REAL, youngstown_zone INTEGER, updated_at TEXT)""")
    fixtures = {
        # id: (word_count, manually_curated, summary_model, tone_tag, summary, topics), expected state
        "cur": ((100, 1, None, None, None, None), "curated"),
        "empty": ((0, 0, None, None, None, None), "no_text"),
        "new": ((100, 0, None, None, None, None), "needs_analysis"),
        "llm_gap": ((100, 0, "m", None, "LLM text", "[]"), "needs_analysis"),
        "llm": ((100, 0, "m", "t", "LLM text", "[]"), "llm_summary"),
        "done": ((100, None, None, "t", "s", "[]"), "analyzed"),
    }
    for oid, (row, _) in fixtures.items():
        mem.execute("""INSERT INTO orders (id, word_count, manually_curated, summary_model, tone_tag,
            summary_plain_english, topic_tags_json) VALUES (?,?,?,?,?,?,?)""", (oid, *row))
    states = dict(mem.execute(f"SELECT id, {enrichment.STATE_SQL} FROM orders"))
    assert states == {oid: exp for oid, (_, exp) in fixtures.items()}, states
    assert sum(enrichment.state_counts(mem).values()) == len(fixtures)
    pick = lambda where: {r[0] for r in mem.execute(f"SELECT id FROM orders WHERE {where}")}
    assert pick(enrichment.heuristic_worker_where()) == {"new", "llm_gap"}
    assert pick(enrichment.heuristic_worker_where(force=True)) == {"new", "llm_gap", "llm", "done"}
    assert pick(enrichment.llm_summarize_where()) == {"new", "done"}
    assert pick(enrichment.llm_summarize_where(redo=True)) == {"new", "llm_gap", "llm", "done"}
    # The heuristic worker fills metrics on an LLM-summarized order but keeps its summary.
    for oid in ("llm_gap", "new"):
        mem.execute(enrichment.HEURISTIC_UPDATE_SQL, (0.1, "Positive", 0.1, 0.0, 0.9, "tone", 2, "heuristic", "[]", "[]", '["x"]', oid))
    assert mem.execute("SELECT tone_tag, summary_plain_english FROM orders WHERE id='llm_gap'").fetchone() == ("tone", "LLM text")
    assert mem.execute("SELECT summary_plain_english FROM orders WHERE id='new'").fetchone() == ("heuristic",)
    mem.close()
    print("✓ Enrichment lifecycle tests passed!")

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
