"""Parses Federal Register executive-order disposition notes (the
"Revoked by: EO 14148, January 20, 2025" lines stored in orders.eo_notes)
into structured relations, then resolves a current status for every order.

The notes are hand-maintained by the Office of the Federal Register and are
inconsistent ("Suspersedes", "Amend by", stray semicolons, "(in part)" in
several positions), so parsing is deliberately tolerant. Status for orders
that predate Federal Register tracking (pre-1994) is inferred from later
orders' outbound notes ("Revokes: EO 11063").
"""
import re

# Label -> (relation, direction). "in" means another order acted on this one;
# "out" means this order acted on another.
_LABELS = [
    (r"revoked\s*(?:\(?in part\)?)?\s*(?:and supplemented)?\s*by", "revoked", "in"),
    (r"rescinded\s*by", "revoked", "in"),
    (r"superseded\s*(?:\(?in part\)?)?\s*by", "superseded", "in"),
    (r"suspended\s*by", "suspended", "in"),
    (r"amend(?:ed)?\s*by", "amended", "in"),
    (r"continued\s*by", "continued", "in"),
    (r"reinstated\s*by", "reinstated", "in"),
    (r"supersedes\s*or\s*revokes", "revoked", "out"),
    (r"(?:partially\s*)?revokes(?:\s*in part)?(?:\s*and supplements)?", "revoked", "out"),
    (r"rescinds", "revoked", "out"),
    (r"terminates", "revoked", "out"),
    (r"(?:partially\s*)?su(?:s)?persedes(?:\s*\(?in part\)?)?", "superseded", "out"),
    (r"suspends", "suspended", "out"),
    (r"amends", "amended", "out"),
    (r"continues(?:\s*certain committee established by)?", "continued", "out"),
    (r"reinstates", "reinstated", "out"),
    (r"supplements", "supplemented", "out"),
    (r"s?ee", "see", "out"),
]
_LABEL_RE = re.compile(
    r"(?:^|[;\n]|\s)(" + "|".join(f"(?:{p})" for p, _, _ in _LABELS) + r")\s*:",
    re.IGNORECASE,
)
_LABEL_LOOKUP = [(re.compile(rf"^{p}$", re.IGNORECASE), rel, direction) for p, rel, direction in _LABELS]
_EO_RE = re.compile(
    r"EO\s*(\d{3,5})(?:-([A-Z]))?(?:,?\s*(?:of\s+)?([A-Z][a-z]+\.?\s+\d{1,2},?\s+\d{4}))?(\s*\(in part\))?",
)


def _classify_label(label):
    label = re.sub(r"\s+", " ", label.strip())
    for pattern, rel, direction in _LABEL_LOOKUP:
        if pattern.match(label):
            return rel, direction
    return None, None


def parse_notes(notes):
    """Returns a list of {relation, direction, eo, date, partial} dicts."""
    if not notes:
        return []
    text = notes.replace("\r\n", "\n")
    matches = list(_LABEL_RE.finditer(text))
    relations = []
    for i, m in enumerate(matches):
        rel, direction = _classify_label(m.group(1))
        if not rel:
            continue
        segment_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        segment = text[m.end():segment_end]
        label_partial = bool(re.search(r"in part|partially", m.group(1), re.IGNORECASE))
        for eo in _EO_RE.finditer(segment):
            relations.append({
                "relation": rel,
                "direction": direction,
                "eo": int(eo.group(1)),
                "date": (eo.group(3) or "").strip() or None,
                "partial": label_partial or bool(eo.group(4)),
            })
    return relations


_STATUS_BY_RELATION = {
    "revoked": ("Revoked", "Partially revoked"),
    "superseded": ("Superseded", "Partially superseded"),
    "suspended": ("Suspended", "Suspended"),
}


def build_dispositions(orders):
    """orders: iterable of dicts with id, eo_number, eo_notes, and optionally
    eo_suffix (set for "-A" orders, which never appear in FR notes). Returns
    {order_id: disposition dict or None}."""
    by_number = {}
    for o in orders:
        if o.get("eo_number") and not o.get("eo_suffix"):
            by_number.setdefault(o["eo_number"], o)

    # EO number -> list of inbound actions {relation, eo, date, partial}
    inbound = {}
    outbound = {}
    for o in orders:
        own_number = o.get("eo_number")
        for r in parse_notes(o.get("eo_notes")):
            if r["eo"] == own_number:
                continue
            if r["direction"] == "in" and own_number and not o.get("eo_suffix"):
                inbound.setdefault(own_number, []).append(
                    {"relation": r["relation"], "eo": r["eo"], "date": r["date"], "partial": r["partial"]}
                )
            elif r["direction"] == "out":
                outbound.setdefault(o["id"], []).append(
                    {"relation": r["relation"], "eo": r["eo"], "date": r["date"], "partial": r["partial"]}
                )
                if own_number and r["relation"] != "see":
                    inbound.setdefault(r["eo"], []).append(
                        {"relation": r["relation"], "eo": own_number, "date": None, "partial": r["partial"]}
                    )

    def dedupe(items):
        seen = {}
        for item in items:
            key = (item["relation"], item["eo"])
            if key in seen:
                seen[key]["partial"] = seen[key]["partial"] and item["partial"]
                seen[key]["date"] = seen[key]["date"] or item["date"]
            else:
                seen[key] = dict(item)
        return sorted(seen.values(), key=lambda x: (x["relation"], x["eo"]))

    def link(item):
        target = by_number.get(item["eo"])
        return {**item, "id": target["id"] if target else None}

    result = {}
    for o in orders:
        own_number = o.get("eo_number")
        ins = dedupe(inbound.get(own_number, [])) if own_number and not o.get("eo_suffix") else []
        outs = dedupe(outbound.get(o["id"], []))
        if not ins and not outs:
            result[o["id"]] = None
            continue

        status = None
        # Reinstatement by a later-numbered order than every revocation undoes it.
        revokers = [i["eo"] for i in ins if i["relation"] in _STATUS_BY_RELATION and not i["partial"]]
        reinstaters = [i["eo"] for i in ins if i["relation"] == "reinstated"]
        if revokers and reinstaters and max(reinstaters) > max(revokers):
            status = "Reinstated"
        else:
            for rel in ("revoked", "superseded", "suspended"):
                full = [i for i in ins if i["relation"] == rel and not i["partial"]]
                if full:
                    status = _STATUS_BY_RELATION[rel][0]
                    break
            if not status:
                for rel in ("revoked", "superseded"):
                    if any(i["relation"] == rel for i in ins):
                        status = _STATUS_BY_RELATION[rel][1]
                        break
            if not status and any(i["relation"] == "amended" for i in ins):
                status = "Amended"

        result[o["id"]] = {
            "status": status,
            "inbound": [link(i) for i in ins],
            "outbound": [link(i) for i in outs],
        }
    return result
