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

from db import init_db, get_connection
from constitutional_engine import analyze_constitutional_sentiment, generate_statesman_summary
from topics import classify_topics
from export_site_data import export_all
from sync_orders import export_stats_json

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

def process_single_order(row: tuple) -> tuple:
    """
    Worker task: takes a DB row and computes constitutional sentiment and statesman summary.
    Row tuple: (id, title, president_name, signing_date, full_text, word_count)
    """
    order_id, title, pres_name, sign_date, full_text, word_count = row
    text = full_text or ""
    w_count = word_count or len(text.split())

    # 1. Analyze Constitutional Sentiment strictly through Framers' prism
    sentiment = analyze_constitutional_sentiment(text, title or "")

    # 2. Generate Constitutional Statesman Summary & Directives
    summary_data = generate_statesman_summary(
        title=title or "Executive Order",
        president_name=pres_name or "the President",
        signing_date=sign_date or "",
        full_text=text,
        word_count=w_count,
        metrics=sentiment
    )

    # 3. Classify into the controlled topic/category taxonomy
    topic_tags = classify_topics(f"{title or ''} {text}")

    # Return tuple for DB update:
    # (sentiment_compound, sentiment_pos, sentiment_neg, sentiment_neu, sentiment_valence,
    #  summary_plain_english, key_directives_json, who_it_affects_json, tone_tag,
    #  topic_tags_json, id)
    return (
        sentiment["sentiment_compound"],
        sentiment["sentiment_pos"],
        sentiment["sentiment_neg"],
        sentiment["sentiment_neu"],
        sentiment["sentiment_valence"],
        summary_data["summary_plain_english"],
        json.dumps(summary_data["key_directives"]),
        json.dumps(summary_data["who_it_affects"]),
        summary_data["tone_tag"],
        json.dumps(topic_tags),
        order_id
    )

def run_batch_worker(batch_size=300, workers=4, limit=None, force=False):
    logging.info("=================================================================")
    logging.info("Starting Constitutional Statesman Sentiment & Summarization Batch Worker")
    logging.info("Prism: United States Constitution (Articles I-VII) & Amendments")
    logging.info(f"Configuration: batch_size={batch_size}, workers={workers}, force={force}, limit={limit}")
    logging.info("=================================================================")

    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    # Query candidate orders
    if force:
        where_clause = "WHERE full_text IS NOT NULL AND length(full_text) > 0"
    else:
        where_clause = (
            "WHERE (summary_plain_english IS NULL OR length(summary_plain_english) = 0 "
            "OR topic_tags_json IS NULL) AND full_text IS NOT NULL AND length(full_text) > 0"
        )

    count_query = f"SELECT COUNT(*) FROM orders {where_clause}"
    cursor.execute(count_query)
    total_to_process = cursor.fetchone()[0]

    if limit and limit > 0:
        total_to_process = min(total_to_process, limit)

    logging.info(f"Total executive orders queued for constitutional evaluation: {total_to_process}")

    if total_to_process == 0:
        logging.info("No unsummarized executive orders found in database. Exiting.")
        conn.close()
        return

    fetch_query = f"""
        SELECT id, title, president_name, signing_date, full_text, word_count 
        FROM orders 
        {where_clause}
        ORDER BY signing_date DESC, id DESC
    """
    if limit and limit > 0:
        fetch_query += f" LIMIT {limit}"

    cursor.execute(fetch_query)
    
    processed_count = 0
    start_time = time.time()
    
    update_sql = """
        UPDATE orders SET
            sentiment_compound = ?,
            sentiment_pos = ?,
            sentiment_neg = ?,
            sentiment_neu = ?,
            sentiment_valence = ?,
            summary_plain_english = ?,
            key_directives_json = ?,
            who_it_affects_json = ?,
            tone_tag = ?,
            topic_tags_json = ?
        WHERE id = ?
    """

    while True:
        rows = cursor.fetchmany(batch_size)
        if not rows:
            break

        batch_t0 = time.time()
        
        # Parallel execution across CPU threads
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
    logging.info("Generating final static datasets for Astro...")
    export_stats_json()
    export_all()
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
