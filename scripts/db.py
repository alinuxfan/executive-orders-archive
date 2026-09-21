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
        
        raw_metadata_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_orders_eo_number ON orders(eo_number);
    CREATE INDEX IF NOT EXISTS idx_orders_president ON orders(president_slug);
    CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(signing_date);
    CREATE INDEX IF NOT EXISTS idx_orders_source ON orders(source);
    """)

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
        "tone_tag", "raw_metadata_json"
    ]
    
    placeholders = ", ".join([f":{f}" for f in fields])
    update_clause = ", ".join([f"{f} = excluded.{f}" for f in fields if f != "id"])
    
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

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)
