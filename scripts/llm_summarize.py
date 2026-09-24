"""Optional: replaces the extractive plain-English summary, key directives,
and affected-entity list with Claude-written ones, via the Message Batches
API (50% of standard token prices, results within ~1 hour, 24h max).

Not run by the sync GitHub Action. New orders still get the free extractive
summary from batch_constitutional_worker.py; run this afterwards to upgrade
them. The existing "Constitutional Assessment:" paragraph is kept, and
hand-curated orders (manually_curated = 1) are never touched.

    pip install anthropic          # plus credentials: ANTHROPIC_API_KEY or `ant auth login`
    PYTHONPATH=scripts python scripts/llm_summarize.py --dry-run            # count + token estimate, no API calls
    PYTHONPATH=scripts python scripts/llm_summarize.py --limit 25           # submit a small batch and wait
    PYTHONPATH=scripts python scripts/llm_summarize.py --resume msgbatch_…  # collect a batch submitted earlier
    PYTHONPATH=scripts python scripts/export_site_data.py && PYTHONPATH=scripts python scripts/build_search_index.py
"""
import argparse
import json
import sys
import time
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from db import init_db, get_connection

DEFAULT_MODEL = "claude-opus-5"
STATE_FILE = _SCRIPTS_DIR.parent / "data" / "llm_batch_state.json"
# Batches accept up to 100,000 requests / 256 MB; stay well under the size cap
# since some orders run to tens of thousands of words.
MAX_BATCH_BYTES = 200 * 1024 * 1024

SYSTEM_PROMPT = """You write plain-English explainers of United States presidential executive orders for a non-partisan public archive read by students, journalists, and lawyers.

Given one order's title, president, signing date, and full text, produce:
- summary: 2-3 short paragraphs (separated by a blank line, 90-200 words total) saying what the order actually does, who must do what, and any deadlines, amounts, places, or named people. Lead with the concrete effect. Explain legal terms in everyday words. Describe; do not praise, criticize, or speculate about motives or consequences beyond the text.
- key_directives: 1-5 of the order's operative commands, most important first. Each has a short title (2-6 words, Title Case, e.g. "Visa Wage Data Review") and a one-sentence description in plain English naming the responsible official or agency.
- who_it_affects: 2-5 groups the order directly affects (e.g. "Department of Labor", "H-1B visa employers", "Federal civil service employees"), most directly affected first.

Old orders are often a single sentence (a land withdrawal, a civil-service exemption for one named person). Keep those summaries to one short paragraph and one directive rather than padding. If the text is garbled or missing, summarize only what the title and any legible text support."""

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "key_directives": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["title", "description"],
                "additionalProperties": False,
            },
        },
        "who_it_affects": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["summary", "key_directives", "who_it_affects"],
    "additionalProperties": False,
}


def select_orders(limit, redo):
    conn = get_connection()
    where = "word_count > 0 AND COALESCE(manually_curated, 0) = 0"
    if not redo:
        where += " AND summary_model IS NULL"
    sql = f"""SELECT id, title, president_name, signing_date, full_text, summary_plain_english
              FROM orders WHERE {where} ORDER BY signing_date DESC"""
    if limit:
        sql += f" LIMIT {int(limit)}"
    rows = [dict(r) for r in conn.execute(sql)]
    conn.close()
    return rows


def user_prompt(order):
    return (
        f"Title: {order['title']}\n"
        f"President: {order['president_name']}\n"
        f"Signed: {order['signing_date'] or 'unknown'}\n\n"
        f"<order_text>\n{order['full_text']}\n</order_text>"
    )


def build_params(order, model, effort):
    return {
        "model": model,
        "max_tokens": 16000,
        "system": SYSTEM_PROMPT,
        "thinking": {"type": "adaptive"},
        "output_config": {"effort": effort, "format": {"type": "json_schema", "schema": OUTPUT_SCHEMA}},
        "messages": [{"role": "user", "content": user_prompt(order)}],
    }


def submit(client, orders, model, effort):
    """Submits one or more batches; returns {batch_id: {custom_id: order}}."""
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    submitted = {}
    requests, mapping, chunk_bytes = [], {}, 0

    def flush():
        batch = client.messages.batches.create(requests=requests)
        submitted[batch.id] = dict(mapping)

    for order in orders:
        params = build_params(order, model, effort)
        size = len(json.dumps(params))
        if requests and chunk_bytes + size > MAX_BATCH_BYTES:
            flush()
            requests, mapping, chunk_bytes = [], {}, 0
        # custom_id allows only [a-zA-Z0-9_-] up to 64 chars, so use a position
        # key rather than the order id (which can exceed 64 chars).
        custom_id = f"order-{len(mapping)}"
        requests.append(Request(custom_id=custom_id, params=MessageCreateParamsNonStreaming(**params)))
        mapping[custom_id] = order
        chunk_bytes += size
    if requests:
        flush()
    return submitted


def wait_for(client, batch_id):
    while True:
        batch = client.messages.batches.retrieve(batch_id)
        if batch.processing_status == "ended":
            return batch
        counts = batch.request_counts
        print(f"  {batch_id}: {counts.processing} processing, {counts.succeeded} succeeded, {counts.errored} errored")
        time.sleep(60)


def keep_assessment(existing_summary):
    """The engine's "Constitutional Assessment:" paragraph, kept under the new summary."""
    for paragraph in (existing_summary or "").split("\n\n"):
        if paragraph.startswith("Constitutional Assessment:"):
            return paragraph
    return ""


def collect(client, batch_id, id_map, model):
    conn = get_connection()
    written = failed = 0
    for result in client.messages.batches.results(batch_id):
        order = id_map.get(result.custom_id)
        if order is None:
            continue
        if result.result.type != "succeeded":
            print(f"  {order['id']}: {result.result.type}")
            failed += 1
            continue
        message = result.result.message
        if message.stop_reason != "end_turn":
            print(f"  {order['id']}: stop_reason={message.stop_reason}; skipped")
            failed += 1
            continue
        text = next((b.text for b in message.content if b.type == "text"), "")
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            print(f"  {order['id']}: unparseable output; skipped")
            failed += 1
            continue
        summary = data["summary"].strip()
        assessment = keep_assessment(order["summary_plain_english"])
        if assessment:
            summary = f"{summary}\n\n{assessment}"
        conn.execute(
            """UPDATE orders SET summary_plain_english = ?, key_directives_json = ?, who_it_affects_json = ?,
                   summary_model = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?""",
            (summary, json.dumps(data["key_directives"]), json.dumps(data["who_it_affects"]), model, order["id"]),
        )
        written += 1
    conn.commit()
    conn.close()
    return written, failed


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of orders to summarize (newest first)")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--effort", default="medium", choices=["low", "medium", "high", "xhigh", "max"])
    parser.add_argument("--redo", action="store_true", help="Also regenerate orders that already have an LLM summary")
    parser.add_argument("--dry-run", action="store_true", help="Report what would be submitted; no API calls")
    parser.add_argument("--resume", metavar="BATCH_ID", help="Collect results for a previously submitted batch")
    args = parser.parse_args()

    init_db()

    if args.resume:
        state = json.loads(STATE_FILE.read_text())
        if args.resume not in state["batches"]:
            sys.exit(f"{args.resume} is not in {STATE_FILE}")
        orders_by_id = {o["id"]: o for o in select_orders(None, redo=True)}
        id_map = {cid: orders_by_id[oid] for cid, oid in state["batches"][args.resume].items() if oid in orders_by_id}
        batch_ids = [args.resume]
        model = state["model"]
    else:
        orders = select_orders(args.limit, args.redo)
        total_chars = sum(len(o["full_text"] or "") for o in orders)
        # ~4 characters per token for English prose; the system prompt adds ~350 tokens per request.
        est_input_tokens = total_chars / 4 + 350 * len(orders)
        print(f"{len(orders)} orders selected, ~{est_input_tokens / 1e6:.1f}M input tokens before thinking/output.")
        if args.dry_run or not orders:
            return
        model = args.model

    try:
        import anthropic
    except ImportError:
        sys.exit("The anthropic package is required: pip install anthropic")
    client = anthropic.Anthropic()

    if not args.resume:
        submitted = submit(client, orders, model, args.effort)
        batch_ids = list(submitted)
        state = {"model": model, "batches": {bid: {cid: o["id"] for cid, o in m.items()} for bid, m in submitted.items()}}
        STATE_FILE.write_text(json.dumps(state))
        print(f"Submitted {', '.join(batch_ids)} (state saved to {STATE_FILE}; resume with --resume BATCH_ID).")
    else:
        submitted = {args.resume: id_map}

    for batch_id in batch_ids:
        wait_for(client, batch_id)
        written, failed = collect(client, batch_id, submitted[batch_id], model)
        print(f"{batch_id}: wrote {written} summaries, {failed} failed or skipped.")
    print("Re-export to publish: export_site_data.py, then build_search_index.py.")


if __name__ == "__main__":
    main()
