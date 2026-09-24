#!/usr/bin/env python3
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from snippets import operative_snippet

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

# Ranked by in-document frequency; past ~30 the tail is mostly incidental words
# that add index weight (downloaded by every /orders and /search visitor)
# without improving recall much.
MAX_KEYWORDS_PER_ORDER = 30


def extract_keywords(full_text, exclude_text=""):
    if not full_text:
        return ""
    # Words already present in the title/snippet are searchable there; don't repeat them.
    already_indexed = set(TOKEN_RE.findall(exclude_text.lower()))
    tokens = [t for t in TOKEN_RE.findall(full_text.lower()) if t not in STOPWORDS and t not in already_indexed]
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
    # Body keywords live in a parallel array (same order as search_index.json)
    # that the client only fetches once a text query is typed, so browsing and
    # filtering /orders doesn't download them.
    keywords_path = os.path.join(root, 'public', 'search_keywords.json')

    if not os.path.exists(source_path):
        print("Warning: site_orders.json not found, skipping index generation")
        return

    with open(source_path, 'r', encoding='utf-8') as f:
        orders = json.load(f)

    stripped = []
    keywords = []
    for o in orders:
        snippet = operative_snippet(o.get('full_text'), o.get('title'), 160)
        entry = {
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
            'snip': snippet,
        }
        keywords.append(extract_keywords(o.get('full_text'), f"{o['title']} {snippet}"))
        # Optional fields are omitted when empty to keep the index small.
        if o.get('eo_suffix'):
            entry['sfx'] = o['eo_suffix']
        if o.get('eo_status'):
            entry['st'] = o['eo_status']
        stripped.append(entry)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(stripped, f, separators=(',', ':'))
    with open(keywords_path, 'w', encoding='utf-8') as f:
        json.dump(keywords, f, separators=(',', ':'))

    print(f"Generated {output_path} with {len(stripped)} indexed orders ({os.path.getsize(output_path)/1024/1024:.2f} MB)"
          f" + keywords ({os.path.getsize(keywords_path)/1024/1024:.2f} MB)")


if __name__ == '__main__':
    main()
