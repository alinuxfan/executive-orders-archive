"""Explicit enrichment lifecycle for an order row.

Every order is in exactly one of these states, derived from its columns (first
match wins, in this order):

    curated         manually_curated = 1. Frozen: no script may rewrite it.
    no_text         word_count is 0/NULL. Nothing to analyze until sync_orders.py
                    fetches a body (it retries on every run).
    needs_analysis  Has text, but tone_tag / summary_plain_english /
                    topic_tags_json is missing. batch_constitutional_worker.py
                    picks these up.
    llm_summary     Analyzed, and summary/directives/who-it-affects were written
                    by llm_summarize.py (summary_model is set).
    analyzed        Analyzed by the heuristic engine only. llm_summarize.py
                    picks these up.

Ownership of the summary fields (summary_plain_english, key_directives_json,
who_it_affects_json):
    - curated orders: the human. Nothing writes them.
    - summary_model set: llm_summarize.py. The heuristic worker may still fill in
      metrics (sentiment, tone, zone, topics) but must keep these three fields.
    - otherwise: batch_constitutional_worker.py.

Run this module to see how many orders are in each state:

    PYTHONPATH=scripts python scripts/enrichment.py
"""

CURATED = "curated"
NO_TEXT = "no_text"
NEEDS_ANALYSIS = "needs_analysis"
LLM_SUMMARY = "llm_summary"
ANALYZED = "analyzed"

STATES = (CURATED, NO_TEXT, NEEDS_ANALYSIS, LLM_SUMMARY, ANALYZED)

IS_CURATED = "COALESCE(manually_curated, 0) = 1"
NOT_CURATED = "COALESCE(manually_curated, 0) = 0"
HAS_TEXT = "COALESCE(word_count, 0) > 0"
MISSING_ANALYSIS = "(tone_tag IS NULL OR summary_plain_english IS NULL OR topic_tags_json IS NULL)"
# Summary fields belong to someone other than the heuristic worker.
SUMMARY_PROTECTED = f"({IS_CURATED} OR summary_model IS NOT NULL)"

STATE_SQL = f"""CASE
    WHEN {IS_CURATED} THEN '{CURATED}'
    WHEN NOT ({HAS_TEXT}) THEN '{NO_TEXT}'
    WHEN {MISSING_ANALYSIS} THEN '{NEEDS_ANALYSIS}'
    WHEN summary_model IS NOT NULL THEN '{LLM_SUMMARY}'
    ELSE '{ANALYZED}'
END"""

# batch_constitutional_worker.py's write. Summary fields are only written when the
# heuristic worker owns them (not SUMMARY_PROTECTED); metrics are always refreshed.
# Parameter order matches process_single_order()'s return tuple.
HEURISTIC_UPDATE_SQL = f"""
    UPDATE orders
    SET
        sentiment_compound = ?,
        sentiment_valence = ?,
        sentiment_pos = ?,
        sentiment_neg = ?,
        sentiment_neu = ?,
        tone_tag = ?,
        youngstown_zone = ?,
        summary_plain_english = CASE WHEN {SUMMARY_PROTECTED} THEN summary_plain_english ELSE ? END,
        key_directives_json = CASE WHEN {SUMMARY_PROTECTED} THEN key_directives_json ELSE ? END,
        who_it_affects_json = CASE WHEN {SUMMARY_PROTECTED} THEN who_it_affects_json ELSE ? END,
        topic_tags_json = ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
"""


def heuristic_worker_where(force=False):
    """Rows batch_constitutional_worker.py should (re)analyze.

    Default: needs_analysis only. With force: every non-curated row with text.
    Either way the worker's UPDATE must keep summary fields where
    SUMMARY_PROTECTED holds (HEURISTIC_UPDATE_SQL does this).
    """
    where = f"{HAS_TEXT} AND {NOT_CURATED}"
    if not force:
        where += f" AND {MISSING_ANALYSIS}"
    return where


def llm_summarize_where(redo=False):
    """Rows llm_summarize.py should summarize. Default skips existing LLM summaries."""
    where = f"{HAS_TEXT} AND {NOT_CURATED}"
    if not redo:
        where += " AND summary_model IS NULL"
    return where


def state_counts(conn):
    """Returns {state: count} for every state (zero-filled)."""
    counts = dict.fromkeys(STATES, 0)
    for state, n in conn.execute(f"SELECT {STATE_SQL} AS state, COUNT(*) FROM orders GROUP BY state"):
        counts[state] = n
    return counts


def main():
    from db import get_connection

    conn = get_connection()
    counts = state_counts(conn)
    conn.close()
    width = max(len(s) for s in STATES)
    for state in STATES:
        print(f"{state:<{width}}  {counts[state]:>6}")
    print(f"{'total':<{width}}  {sum(counts.values()):>6}")


if __name__ == "__main__":
    main()
