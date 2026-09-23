import argparse
import concurrent.futures
import datetime
import json
import logging
import os
import sys
import time
from pathlib import Path

# Ensure scripts directory is in sys.path
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from db import init_db, get_connection, vacuum_db
from constitutional_engine import analyze_constitutional_sentiment, generate_statesman_summary
from topics import classify_topics
from export_site_data import export_all
from sync_orders import export_stats_json
from build_search_index import main as build_search_index_main

ROOT_DIR = SCRIPTS_DIR.parent
DATA_DIR = ROOT_DIR / "data"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(DATA_DIR / "constitutional_batch.log", mode="a", encoding="utf-8")
    ]
)

def process_single_order(row):
    order_id, title, full_text, pres_name, s_date, w_count = row
    
    # 1. Constitutional Analysis
    metrics = analyze_constitutional_sentiment(full_text or "", title or "")
    
    # 2. Statesman Plain-English Summarization & Directives
    summary_data = generate_statesman_summary(
        title=title or "",
        president_name=pres_name or "Unknown",
        signing_date=s_date or "",
        full_text=full_text or "",
        word_count=w_count or 0,
        metrics=metrics
    )

    # 3. Controlled Topic Classification
    topic_tags = classify_topics(title or "", full_text or "")
    
    return (
        metrics["sentiment_compound"],
        metrics["sentiment_valence"],
        metrics["sentiment_pos"],
        metrics["sentiment_neg"],
        metrics["sentiment_neu"],
        metrics["tone_tag"],
        summary_data["summary_plain_english"],
        json.dumps(summary_data["key_directives"]),
        json.dumps(summary_data["who_it_affects"]),
        json.dumps(topic_tags),
        order_id
    )

def run_batch_worker(batch_size=200, workers=4, limit=None, force=False):
    logging.info("=================================================================")
    logging.info("Starting High-Performance Multithreaded Constitutional Engine")
    logging.info(f"Configuration: workers={workers}, batch_size={batch_size}, force={force}")
    logging.info("=================================================================")
    
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    if force:
        where_clause = "WHERE word_count > 0"
    else:
        # Process any order that lacks tone_tag OR summary_plain_english OR topic_tags_json
        where_clause = "WHERE word_count > 0 AND (tone_tag IS NULL OR summary_plain_english IS NULL OR topic_tags_json IS NULL)"

    limit_clause = f"LIMIT {limit}" if limit else ""

    query = f"""
        SELECT id, title, full_text, president_name, signing_date, word_count 
        FROM orders 
        {where_clause}
        ORDER BY signing_date DESC
        {limit_clause}
    """

    cursor.execute(query)
    rows_to_process = cursor.fetchall()
    total_to_process = len(rows_to_process)

    logging.info(f"Orders requiring constitutional evaluation: {total_to_process}")

    if total_to_process == 0:
        logging.info("No orders need constitutional analysis. Database is 100% enriched!")
        conn.close()
        return

    update_sql = """
        UPDATE orders 
        SET 
            sentiment_compound = ?,
            sentiment_valence = ?,
            sentiment_pos = ?,
            sentiment_neg = ?,
            sentiment_neu = ?,
            tone_tag = ?,
            summary_plain_english = ?,
            key_directives_json = ?,
            who_it_affects_json = ?,
            topic_tags_json = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """

    processed_count = 0
    start_time = time.time()

    # Process in batches
    for i in range(0, total_to_process, batch_size):
        batch_t0 = time.time()
        rows = rows_to_process[i:i + batch_size]
        
        # Parallel NLP computation
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            results = list(executor.map(process_single_order, rows))

        # Atomic commit to SQLite
        update_conn = get_connection()
        update_cur = update_conn.cursor()
        update_cur.executemany(update_sql, results)
        update_conn.commit()
        update_conn.close()

        processed_count += len(results)
        elapsed = time.time() - start_time
        rate = processed_count / elapsed if elapsed > 0 else 0
        pct = (processed_count / total_to_process) * 100
        batch_duration = time.time() - batch_t0

        logging.info(
            f"Progress: [{processed_count}/{total_to_process}] ({pct:.1f}%) | "
            f"Batch: {len(results)} in {batch_duration:.2f}s | "
            f"Overall Rate: {rate:.1f} orders/sec"
        )

        # Export intermediate site data every 1000 orders
        if processed_count % 1000 == 0 or processed_count == total_to_process:
            logging.info("Syncing site JSON datasets with latest constitutional evaluations...")
            export_stats_json()
            export_all()

    conn.close()
    total_time = time.time() - start_time
    logging.info("=================================================================")
    logging.info(f"Constitutional Batch Evaluation Completed in {total_time:.2f}s!")
    logging.info(f"Processed: {processed_count} orders at {processed_count/max(0.1, total_time):.1f} orders/second.")
    logging.info("Generating final static datasets and search index for Astro...")
    export_stats_json()
    export_all()
    build_search_index_main()
    vacuum_db()
    logging.info("All site datasets successfully updated and synchronized!")

def main():
    parser = argparse.ArgumentParser(description="Constitutional Statesman Sentiment & Summarization Batch Worker")
    parser.add_argument("--batch-size", type=int, default=300, help="Number of records per DB transaction batch")
    parser.add_argument("--workers", type=int, default=4, help="Number of concurrent worker threads")
    parser.add_argument("--limit", type=int, default=None, help="Optional maximum number of orders to process")
    parser.add_argument("--force", action="store_true", help="Force re-evaluation of already processed orders")
    args = parser.parse_args()

    run_batch_worker(
        batch_size=args.batch_size,
        workers=args.workers,
        limit=args.limit,
        force=args.force
    )

if __name__ == "__main__":
    main()
