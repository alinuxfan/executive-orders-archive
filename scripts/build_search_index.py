#!/usr/bin/env python3
import json
import os

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    summary_path = os.path.join(root, 'data', 'site_orders_summary.json')
    output_path = os.path.join(root, 'public', 'search_index.json')
    
    if not os.path.exists(summary_path):
        print("Warning: site_orders_summary.json not found, skipping index generation")
        return

    with open(summary_path, 'r', encoding='utf-8') as f:
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
        'snip': (o.get('snippet') or '')[:140]
    } for o in orders]
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(stripped, f, separators=(',', ':'))
        
    print(f"Generated {output_path} with {len(stripped)} indexed orders ({os.path.getsize(output_path)/1024/1024:.2f} MB)")

if __name__ == '__main__':
    main()
