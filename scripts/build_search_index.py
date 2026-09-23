#!/usr/bin/env python3
import json
import os
import re
from collections import Counter

# Small generic English stopword list. Legal-domain terms (e.g. "hereby",
# "pursuant", "authority") are intentionally left in since users may search
# for them, and EO numbers / president names are already indexed separately.
STOPWORDS = {
    "about", "above", "after", "again", "against", "all", "and", "any", "are",
    "because", "been", "before", "being", "below", "between", "both", "but",
    "cannot", "could", "did", "does", "doing", "down", "during", "each",
    "few", "for", "from", "further", "had", "has", "have", "having", "here",
    "hers", "herself", "him", "himself", "his", "how", "into", "itself",
    "just", "more", "most", "myself", "nor", "not", "now", "off", "once",
    "only", "other", "ours", "ourselves", "over", "own", "same", "she",
    "should", "some", "such", "than", "that", "their", "theirs", "them",
    "themselves", "then", "there", "these", "they", "this", "those",
    "through", "under", "until", "very", "was", "were", "what", "when",
    "where", "which", "while", "who", "whom", "why", "will", "with",
    "would", "your", "yours", "yourself", "yourselves", "shall", "section",
    "title", "order", "president", "executive", "united", "states",
}

TOKEN_RE = re.compile(r"[a-z]{4,}")

MAX_KEYWORDS_PER_ORDER = 60


def extract_keywords(full_text):
    if not full_text:
        return ""
    tokens = [t for t in TOKEN_RE.findall(full_text.lower()) if t not in STOPWORDS]
    if not tokens:
        return ""
    ranked = [word for word, _ in Counter(tokens).most_common(MAX_KEYWORDS_PER_ORDER)]
    return " ".join(ranked)


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Sourced from site_orders.json (not the summary) since full_text is
    # needed to build the keyword index for body/full-text search.
    source_path = os.path.join(root, 'data', 'site_orders.json')
    output_path = os.path.join(root, 'public', 'search_index.json')

    if not os.path.exists(source_path):
        print("Warning: site_orders.json not found, skipping index generation")
        return

    with open(source_path, 'r', encoding='utf-8') as f:
        orders = json.load(f)

    stripped = [{
        'id': o['id'],
        'title': o['title'],
        'pres': o['president_name'],
        'slug': o.get('president_slug', ''),
        'num': o.get('eo_number'),
        'date': o.get('signing_date', '')[:10] if o.get('signing_date') else '',
        'val': o.get('sentiment_valence', ''),
        'comp': round(o.get('sentiment_compound', 0), 2),
        'time': o.get('reading_time_minutes', 1),
        'words': o.get('word_count', 0),
        'tag': o.get('tone_tag', ''),
        'topics': json.loads(o['topic_tags_json']) if o.get('topic_tags_json') else [],
        'snip': (o.get('full_text') or '')[:140],
        'kw': extract_keywords(o.get('full_text')),
    } for o in orders]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(stripped, f, separators=(',', ':'))

    print(f"Generated {output_path} with {len(stripped)} indexed orders ({os.path.getsize(output_path)/1024/1024:.2f} MB)")


if __name__ == '__main__':
    main()
