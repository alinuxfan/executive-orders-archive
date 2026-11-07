import sys
from pathlib import Path
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
import json
import re
from datetime import datetime
from db import get_connection
from dispositions import build_dispositions
from snippets import operative_snippet
from constitutional_engine import classify_youngstown_zone

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
PUBLIC_DIR = ROOT_DIR / "public"

EO_REF_RE = re.compile(r"Executive Order\s*(?:No\.?)?\s*(\d{4,5})", re.IGNORECASE)

MILESTONE_DEFINITIONS = [
    {
        "id": "app-commission-appointing-commissioners-for-surveying-the-district-territory-for-the-permanent",
        "badge": "🇺🇸 Washington #1",
        "shortLabel": "1st Executive Action (1791)",
        "description": "George Washington's survey establishing the permanent capital city of Washington, D.C."
    },
    {
        "id": "app-executive-order-suspension-the-writ-habeas-corpus",
        "badge": "⚖️ Civil War Power",
        "shortLabel": "Lincoln Habeas Corpus (1861)",
        "description": "Abraham Lincoln suspending the writ of habeas corpus during the early outbreak of the American Civil War."
    },
    {
        "id": "app-executive-order-6102-forbidding-the-hoarding-gold-coin-gold-bullion-and-gold-certificates",
        "badge": "💰 Gold Confiscation",
        "shortLabel": "FDR Gold Ban (1933)",
        "description": "Franklin D. Roosevelt prohibiting hoarding of gold coins, bullion, and certificates under Trading with the Enemy Act."
    },
    {
        "id": "app-executive-order-8985-establishing-the-office-censorship-and-prescribing-its-functions-and",
        "badge": "📉 High Constitutional Friction",
        "shortLabel": "FDR Censorship Office (1941)",
        "description": "WWII censorship decree with extreme constitutional friction (-0.91) following the attack on Pearl Harbor."
    },
    {
        "id": "app-executive-order-9066-authorizing-the-secretary-war-prescribe-military-areas",
        "badge": "⚠️ Landmark Friction",
        "shortLabel": "FDR Japanese Internment (1942)",
        "description": "WWII order authorizing the forced internment and removal of Japanese Americans from coastal military zones."
    },
    {
        "id": "app-executive-order-9981-establishing-the-presidents-committee-equality-treatment-and",
        "badge": "🎖️ Military Integration",
        "shortLabel": "Truman Desegregation (1948)",
        "description": "Harry S. Truman desegregating the United States Armed Forces, establishing equality of treatment and opportunity."
    },
    {
        "id": "app-executive-order-10214-prescribing-the-manual-for-courts-martial-united-states-1951",
        "badge": "📚 Longest in US History",
        "shortLabel": "Manual for Courts-Martial (1951)",
        "description": "Harry S. Truman's massive 52,000-word Uniform Code of Military Justice codification."
    },
    {
        "id": "app-executive-order-10340-directing-the-secretary-commerce-take-possession-and-operate-the",
        "badge": "🏛️ Youngstown Precedent",
        "shortLabel": "Youngstown Steel Seizure (1952)",
        "description": "The steel mills seizure struck down in Youngstown v. Sawyer, creating the modern 3-tier presidential power test."
    }
]

def detect_relation(text: str, start: int, end: int) -> str:
    win_start = max(0, start - 140)
    win_end = min(len(text), end + 40)
    ctx = text[win_start:win_end].lower()
    if "revok" in ctx:
        return "Revokes"
    if "rescind" in ctx:
        return "Rescinds"
    if "supersed" in ctx:
        return "Supersedes"
    if "amend" in ctx:
        return "Amends"
    return "References"

def export_all():
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch all orders
    cursor.execute("""
        SELECT id, eo_number, title, president_name, president_slug, signing_date, publication_date,
               source, source_url, pdf_url, word_count, char_count, reading_time_minutes, flesch_kincaid_grade,
               sentiment_compound, sentiment_pos, sentiment_neg, sentiment_neu, sentiment_valence,
               summary_plain_english, key_directives_json, who_it_affects_json, tone_tag,
               youngstown_zone, topic_tags_json, fr_citation, eo_notes, full_text
        FROM orders 
        ORDER BY signing_date DESC, id DESC
    """)
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    orders = []
    reverse_reference_map = {}

    for r in rows:
        d = dict(zip(columns, r))
        # "Executive Order 11359-A—..." shares eo_number 11359 with the unsuffixed
        # order; the suffix disambiguates display labels and cross-reference links.
        suffix = re.match(r"^Executive Order\s*\d+-([A-Z])", d["title"] or "")
        d["eo_suffix"] = suffix.group(1) if suffix else None

        # Precompute Youngstown classification zone if not already present
        zone = d.get("youngstown_zone")
        if not zone:
            zone = classify_youngstown_zone(
                valence=d.get("sentiment_valence") or "",
                compound=d.get("sentiment_compound") or 0.0,
                tone_tag=d.get("tone_tag") or "",
                title=d.get("title") or ""
            )
        d["youngstown_zone"] = zone
        d["zone"] = zone

        orders.append(d)

        # Reverse reference indexing (citations in full_text)
        full_text = d.get("full_text") or ""
        if full_text:
            seen_numbers = set()
            for m in EO_REF_RE.finditer(full_text):
                num = int(m.group(1))
                if not num or num == d.get("eo_number") or num in seen_numbers:
                    continue
                seen_numbers.add(num)
                rel = detect_relation(full_text, m.start(), m.end())
                if num not in reverse_reference_map:
                    reverse_reference_map[num] = []
                # Keep top 8 citations per EO number
                if len(reverse_reference_map[num]) < 8:
                    reverse_reference_map[num].append({
                        "id": d["id"],
                        "eo_number": d.get("eo_number"),
                        "title": d["title"],
                        "president_name": d["president_name"],
                        "president_slug": d.get("president_slug"),
                        "signing_date": d.get("signing_date"),
                        "relation": rel
                    })

    dispositions = build_dispositions(orders)
    for d in orders:
        disposition = dispositions.get(d["id"])
        d["disposition_json"] = json.dumps(disposition, ensure_ascii=False) if disposition else None
        d["eo_status"] = disposition["status"] if disposition else None
        del d["eo_notes"]

    json_kwargs = {"ensure_ascii": False, "separators": (",", ":")}

    # Write site_orders.json
    with open(DATA_DIR / "site_orders.json", "w", encoding="utf-8") as f:
        json.dump(orders, f, **json_kwargs)

    # Write data/reverse_references.json
    with open(DATA_DIR / "reverse_references.json", "w", encoding="utf-8") as f:
        json.dump(reverse_reference_map, f, **json_kwargs)

    # Write site_orders_summary.json
    detail_only_fields = {
        "full_text", "summary_plain_english", "key_directives_json", "who_it_affects_json",
        "sentiment_pos", "sentiment_neg", "sentiment_neu", "char_count", "pdf_url",
        "publication_date", "disposition_json",
    }
    summary_orders = []
    order_by_id = {}
    for o in orders:
        summary_o = {k: v for k, v in o.items() if k not in detail_only_fields}
        summary_o["snippet"] = operative_snippet(o["full_text"], o["title"], 280)
        summary_o["zone"] = o["youngstown_zone"]
        summary_orders.append(summary_o)
        order_by_id[o["id"]] = summary_o

    with open(DATA_DIR / "site_orders_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_orders, f, **json_kwargs)

    # Write public/quick-share-data.json
    now = datetime.now()
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    cur_month = f"{now.month:02d}"
    cur_day = f"{now.day:02d}"
    cur_month_day = f"{cur_month}-{cur_day}"

    today_orders = [
        o for o in summary_orders
        if o.get("signing_date") and o["signing_date"][5:10] == cur_month_day
    ]
    today_orders.sort(key=lambda x: int(x["signing_date"][:4]) if x.get("signing_date") else 0, reverse=True)

    milestone_orders = []
    for m in MILESTONE_DEFINITIONS:
        match = order_by_id.get(m["id"])
        if match:
            milestone_orders.append({
                "badge": m["badge"],
                "shortLabel": m["shortLabel"],
                "description": m["description"],
                "order": {
                    "id": match["id"],
                    "eo_number": match.get("eo_number"),
                    "title": match["title"],
                    "president_name": match["president_name"],
                    "president_slug": match.get("president_slug"),
                    "signing_date": match.get("signing_date"),
                    "sentiment_valence": match.get("sentiment_valence"),
                    "sentiment_compound": match.get("sentiment_compound"),
                    "tone_tag": match.get("tone_tag"),
                    "zone": match.get("zone", 2),
                    "snippet": match.get("snippet", "")
                }
            })

    roulette_seed = [
        {
            "id": o["id"],
            "eo_number": o.get("eo_number"),
            "title": o["title"],
            "president_name": o["president_name"],
            "president_slug": o.get("president_slug"),
            "signing_date": o.get("signing_date"),
            "sentiment_valence": o.get("sentiment_valence"),
            "sentiment_compound": o.get("sentiment_compound"),
            "tone_tag": o.get("tone_tag"),
            "zone": o.get("zone", 2),
            "snippet": o.get("snippet", "")
        }
        for o in (today_orders[:10] + [m["order"] for m in milestone_orders])
    ]

    quick_share_payload = {
        "todayOrders": [
            {
                "id": o["id"],
                "eo_number": o.get("eo_number"),
                "title": o["title"],
                "president_name": o["president_name"],
                "president_slug": o.get("president_slug"),
                "signing_date": o.get("signing_date"),
                "sentiment_valence": o.get("sentiment_valence"),
                "sentiment_compound": o.get("sentiment_compound"),
                "tone_tag": o.get("tone_tag"),
                "zone": o.get("zone", 2),
                "snippet": o.get("snippet", "")
            }
            for o in today_orders
        ],
        "milestones": milestone_orders,
        "rouletteSeed": roulette_seed,
        "dateInfo": {
            "year": now.year,
            "month": cur_month,
            "day": cur_day,
            "monthDay": cur_month_day,
            "monthName": month_names[now.month - 1],
            "dayInt": now.day
        }
    }

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    with open(PUBLIC_DIR / "quick-share-data.json", "w", encoding="utf-8") as f:
        json.dump(quick_share_payload, f, **json_kwargs)

    print(f"Exported {len(orders)} orders to data/site_orders.json, data/site_orders_summary.json, data/reverse_references.json, and public/quick-share-data.json")
    conn.close()

if __name__ == "__main__":
    export_all()
