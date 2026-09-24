"""Extracts the first operative sentence(s) of an executive order, skipping
the parts every order shares: Federal Register page markers, the
"Executive Order N of <date> <title>" header, "Whereas" recitals, the
"By the authority vested in me ... it is hereby ordered:" enacting clause,
and "Section 1. Purpose." headings. Used for listing/search/RSS snippets
and the extractive plain-English summary, where the boilerplate opening
told readers nothing about what the order does.
"""
import re

_PAGE_MARKER_RE = re.compile(r"\(\s*printed page \d+\s*\)", re.IGNORECASE)
_HEADER_RE = re.compile(
    r"^\s*Executive Order\s+\d+(?:-[A-Z])?\s+of\s+[A-Z][a-z]+\.?\s+\d{1,2},\s+\d{4}\s*", re.IGNORECASE
)
_ENACTING_RE = re.compile(
    r"(?:it is hereby ordered|\bhereby order(?: and direct)?\b|I do hereby|it is ordered)"
    r"(?:\s+as follows)?\s*(?::|that|,)?\s*",
    re.IGNORECASE,
)
_NOW_THEREFORE_RE = re.compile(r"Now,?\s*Therefore\s*,?", re.IGNORECASE)
_AUTHORITY_OPENER_RE = re.compile(
    r"^(?:By\s+virtue\s+of|By\s+the\s+authority|Under\s+(?:and\s+by\s+virtue\s+of\s+)?(?:the\s+)?authority|Pursuant\s+to)",
    re.IGNORECASE,
)
# Where the operative clause starts once the "By virtue of the authority vested
# in me by <statutes>," recital ends: a comma followed by a plausible subject.
_CLAUSE_SUBJECT_RE = re.compile(
    r",\s+(?=(?:I[ ,]|Executive Order|[Ss]ection\s+\d|[Tt]he\s|[Ii]t\s+is\s|[Tt]here\s|[Aa]ll\s|[Ee]ach\s|[Aa]ny\s|"
    r"[Pp]aragraph\s|[Ss]chedule\s|[Ss]ubdivision\s|[Rr]ule\s|[Rr]egulations\s|[Ll]ands\s))"
)
# Signature block that closes most pre-1990s orders: "HARRY S. TRUMAN THE WHITE HOUSE, June 22, 1951."
_SIGNATURE_RE = re.compile(r"\s+[A-Z][A-Z. ]{3,}\s+(?:THE WHITE HOUSE|The White House)\b.*$", re.DOTALL)
_CAPS_HEADING_RE = re.compile(r"^(?:[A-Z0-9][A-Z0-9,.'&-]*\s+){2,}(?=[A-Z][a-z]|I\s)")
_HEREBY_RE = re.compile(r"\bhereby\b", re.IGNORECASE)
_SECTION_HEADING_RE = re.compile(
    r"^\s*(?i:Section|Sec\.)\s*1(?:01)?\s*\.?\s*(?:[A-Z][A-Za-z ,;&'-]{0,80}?\.\s+(?![\d]))?"
)
_PART_HEADING_RE = re.compile(r"^\s*(?:Part|Subpart)\s+[IVX\d]+\s*(?:[.—-]+|--)?\s*[A-Z][A-Za-z ,'-]{0,60}?\s+(?=(?i:Section|Sec\.)\s*\d|[A-Z][a-z])")
_ENUMERATOR_RE = re.compile(r"^\s*(?:\((?:a|1|i)\)|1\.(?=\s+[A-Z]))\s*")


def _strip_title(text, title):
    clean_title = re.sub(r"^Executive Order\s*\d*(?:-[A-Z])?\s*[—–-]?\s*", "", title or "", flags=re.IGNORECASE).strip()
    if clean_title and len(clean_title) > 8:
        idx = text.lower().find(clean_title.lower()[:60])
        if 0 <= idx < 80:
            end = idx + len(clean_title)
            return text[end:].lstrip(" .:")
    return text


def operative_text(full_text, title=""):
    """Full text with the shared boilerplate opening removed."""
    text = _PAGE_MARKER_RE.sub(" ", full_text or "")
    text = re.sub(r"\s+", " ", text).strip()
    text = _SIGNATURE_RE.sub("", text)
    header = _HEADER_RE.match(text)
    if header:
        text = _strip_title(text[header.end():], title)

    if text[:10].lower().startswith("whereas"):
        now = _NOW_THEREFORE_RE.search(text[:4000])
        if now:
            text = text[now.end():].lstrip(" ,")
    head = text[:1500]
    enacting = _ENACTING_RE.search(head)
    if enacting and enacting.start() < 1200:
        text = text[enacting.end():]
    elif _AUTHORITY_OPENER_RE.match(text):
        hereby = _HEREBY_RE.search(text[:1200])
        limit = hereby.start() if hereby else 900
        # With a "hereby" to anchor on, the recital ends at the last subject-like
        # comma before it (statute lists like "including X, the National
        # Emergencies Act" produce earlier false starts); otherwise take the first.
        clauses = list(_CLAUSE_SUBJECT_RE.finditer(text[:limit]))
        if clauses:
            text = text[(clauses[-1] if hereby else clauses[0]).end():]
    text = _CAPS_HEADING_RE.sub("", text, count=1)
    text = _PART_HEADING_RE.sub("", text, count=1)
    text = _SECTION_HEADING_RE.sub("", text, count=1)
    text = _ENUMERATOR_RE.sub("", text, count=1)
    text = text.strip(" :;,-—")
    return text[:1].upper() + text[1:] if text else ""


_ABBREV_RE = re.compile(
    r"\b(No|Nos|Sec|Secs|U\.S|U\.S\.C|Stat|Stats|Mr|Mrs|Dr|Gen|Col|Lt|Capt|Maj|Adm|Jr|Sr|St|Co|Corp|Inc|Ltd|"
    r"seq|i\.e|e\.g|Ch|ch|Art|Vol|Tps?|Rs?|sec|secs|par|pars|Ariz|Calif|Colo|Mont|Nev|Wash|Wyo|Ore|Fla|"
    r"Ala|Ark|Okla|Mich|Minn|Wis|Pa|Va|Mex|Dak|Neb|Kans|Tenn|Ky|Md|Del|Conn|Mass|Oreg|Fed|Reg|Ex|Exec|"
    r"approx|viz|etc|[A-Z])\.(?=\s)"
)
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\"“])")


def split_sentences(text):
    """Sentence split that doesn't break on "No. 1234", "U.S.C.", "Claude L. Draper", etc."""
    protected = _ABBREV_RE.sub(lambda m: m.group(0).replace(".", "․"), text)
    return [p.replace("․", ".").strip() for p in _SENTENCE_SPLIT_RE.split(protected) if p.strip()]


def truncate_sentences(text, max_len):
    """Whole sentences up to max_len, falling back to a word-boundary cut."""
    if len(text) <= max_len:
        return text
    kept = ""
    for sentence in split_sentences(text):
        candidate = f"{kept} {sentence}".strip()
        if len(candidate) > max_len:
            break
        kept = candidate
    if len(kept) >= max_len * 0.5:
        return kept
    cut = text[:max_len - 1]
    return cut[:cut.rfind(" ")].rstrip(" ,;:—-") + "…"


def operative_snippet(full_text, title="", max_len=280):
    return truncate_sentences(operative_text(full_text, title), max_len)
