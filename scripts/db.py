import sys
from pathlib import Path
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "orders.sqlite"

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS orders (
        id TEXT PRIMARY KEY,               -- e.g. "fr-2026-19335" or "app-70145"
        eo_number INTEGER,                -- e.g. 14428 (NULL if unnumbered historical)
        title TEXT NOT NULL,
        president_name TEXT NOT NULL,
        president_slug TEXT,
        signing_date TEXT,                -- ISO YYYY-MM-DD
        publication_date TEXT,            -- ISO YYYY-MM-DD
        source TEXT NOT NULL,             -- 'federal_register' | 'presidency_project'
        source_url TEXT,
        pdf_url TEXT,
        full_text TEXT,
        
        -- Length & Complexity Metrics
        word_count INTEGER,
        char_count INTEGER,
        reading_time_minutes INTEGER,
        flesch_kincaid_grade REAL,
        
        -- Sentiment & Tone Metrics
        sentiment_compound REAL,
        sentiment_pos REAL,
        sentiment_neg REAL,
        sentiment_neu REAL,
        sentiment_valence TEXT,           -- 'Positive' | 'Neutral' | 'Urgent/Negative'
        
        -- Plain English Intelligence
        summary_plain_english TEXT,
        key_directives_json TEXT,         -- JSON array of strings
        who_it_affects_json TEXT,         -- JSON array of strings
        tone_tag TEXT,                    -- e.g. 'Regulatory', 'Emergency', 'Directive'
        topic_tags_json TEXT,              -- JSON array of controlled taxonomy topics (scripts/topics.py)
        fr_citation TEXT,                 -- Federal Register citation, e.g. "91 FR 60501"
        eo_notes TEXT,                    -- Federal Register disposition notes ("Revoked by: EO 14148, ...")
        manually_curated INTEGER DEFAULT 0, -- 1 = summary/directives hand-written; batch worker must not regenerate
        summary_model TEXT,               -- set when summary/directives came from scripts/llm_summarize.py (model ID)

        raw_metadata_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_orders_eo_number ON orders(eo_number);
    CREATE INDEX IF NOT EXISTS idx_orders_president ON orders(president_slug);
    CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(signing_date);
    CREATE INDEX IF NOT EXISTS idx_orders_source ON orders(source);

    -- Field-level diff log: records what changed when a resync touches an
    -- order that already existed (e.g. Federal Register corrects a title or
    -- republishes body text). Populated by sync_orders.py, not by the
    -- constitutional enrichment worker.
    CREATE TABLE IF NOT EXISTS order_change_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT NOT NULL,
        field TEXT NOT NULL,
        old_value TEXT,
        new_value TEXT,
        changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_change_log_order ON order_change_log(order_id);
    CREATE INDEX IF NOT EXISTS idx_change_log_time ON order_change_log(changed_at);
    """)

    # CREATE TABLE IF NOT EXISTS doesn't retroactively add columns to a
    # pre-existing table, so newly introduced columns need an explicit
    # idempotent migration here.
    cursor.execute("PRAGMA table_info(orders)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    for column in ("topic_tags_json", "fr_citation", "eo_notes", "summary_model"):
        if column not in existing_columns:
            cursor.execute(f"ALTER TABLE orders ADD COLUMN {column} TEXT")
    if "manually_curated" not in existing_columns:
        cursor.execute("ALTER TABLE orders ADD COLUMN manually_curated INTEGER DEFAULT 0")

    conn.commit()
    conn.close()

def upsert_order(order_dict):
    conn = get_connection()
    cursor = conn.cursor()

    fields = [
        "id", "eo_number", "title", "president_name", "president_slug",
        "signing_date", "publication_date", "source", "source_url", "pdf_url",
        "full_text", "word_count", "char_count", "reading_time_minutes",
        "flesch_kincaid_grade", "sentiment_compound", "sentiment_pos",
        "sentiment_neg", "sentiment_neu", "sentiment_valence",
        "summary_plain_english", "key_directives_json", "who_it_affects_json",
        "tone_tag", "topic_tags_json", "fr_citation", "eo_notes", "raw_metadata_json"
    ]

    # These fields are populated by the constitutional batch worker, not by the
    # routine sync fetch. sync_orders.py always sends NULL/plain-VADER values for
    # them, so a plain overwrite here would silently erase prior enrichment every
    # time a resync re-touches an order still inside its lookback window.
    # tone_tag is only ever set by the batch worker, so "tone_tag already set"
    # is used as the signal that this order has already been constitutionally
    # evaluated and its sentiment/summary fields should be left alone.
    # full_text and fr_citation/eo_notes aren't enriched, but a NULL from a failed
    # body fetch or a sparse API response must not erase previously stored values
    # either (sync_orders.py sends NULL rather than "" when the fetch fails).
    protected_null_coalesce_fields = [
        "summary_plain_english", "key_directives_json", "who_it_affects_json", "tone_tag",
        "topic_tags_json", "full_text", "fr_citation", "eo_notes"
    ]
    protected_if_evaluated_fields = [
        "sentiment_compound", "sentiment_pos", "sentiment_neg", "sentiment_neu", "sentiment_valence"
    ]

    placeholders = ", ".join([f":{f}" for f in fields])

    update_parts = []
    for f in fields:
        if f == "id":
            continue
        if f in protected_null_coalesce_fields:
            update_parts.append(f"{f} = COALESCE(excluded.{f}, {f})")
        elif f in protected_if_evaluated_fields:
            update_parts.append(f"{f} = CASE WHEN tone_tag IS NOT NULL THEN {f} ELSE excluded.{f} END")
        else:
            update_parts.append(f"{f} = excluded.{f}")
    update_clause = ", ".join(update_parts)

    # Ensure all fields are present in dict
    record = {f: order_dict.get(f) for f in fields}

    sql = f"""
    INSERT INTO orders ({", ".join(fields)}, updated_at)
    VALUES ({placeholders}, CURRENT_TIMESTAMP)
    ON CONFLICT(id) DO UPDATE SET
        {update_clause},
        updated_at = CURRENT_TIMESTAMP
    """

    cursor.execute(sql, record)
    conn.commit()
    conn.close()

def vacuum_db():
    """Reclaims free pages left behind by UPDATE/DELETE churn (enrichment
    fields going from NULL to populated, field corrections, etc.) so the file
    on disk tracks its logical data size instead of accumulating slack. Cheap
    at this database's scale (a few seconds even at ~11k rows), so it's run
    at the end of every batch_constitutional_worker.py invocation — which
    already runs twice on every weekday via the sync-orders GitHub Action —
    rather than needing a separate maintenance schedule."""
    conn = get_connection()
    conn.execute("VACUUM")
    conn.close()

def get_order(order_id):
    """Fetch the current row for an order, or None if it doesn't exist yet.
    Used by sync_orders.py to snapshot pre-upsert state for diffing."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# Fields worth flagging when they change on a resync of an already-known
# order — i.e. plausible Federal Register corrections, not routine
# enrichment (those are separately protected in upsert_order above).
TRACKED_DIFF_FIELDS = [
    "title", "eo_number", "president_name", "signing_date",
    "publication_date", "source_url", "pdf_url"
]

def log_field_changes(order_id, old_record, new_record):
    """Diffs old vs. new field values for an existing order and records any
    changes in order_change_log. No-op for brand-new orders (nothing to diff
    against). full_text is tracked by length delta only — the values can be
    tens of thousands of characters, so storing full before/after text isn't
    practical here."""
    if old_record is None:
        return

    changes = []
    for field in TRACKED_DIFF_FIELDS:
        old_val = old_record.get(field)
        new_val = new_record.get(field)
        if new_val is not None and old_val != new_val:
            changes.append((order_id, field, str(old_val) if old_val is not None else None, str(new_val)))

    old_text = old_record.get("full_text") or ""
    new_text = new_record.get("full_text") or ""
    if new_text and old_text != new_text:
        changes.append((order_id, "full_text", f"{len(old_text)} chars", f"{len(new_text)} chars"))

    if not changes:
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO order_change_log (order_id, field, old_value, new_value) VALUES (?, ?, ?, ?)",
        changes
    )
    conn.commit()
    conn.close()
    return changes

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)
