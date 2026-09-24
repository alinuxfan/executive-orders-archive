import re
import json
from typing import Dict, Any, List, Tuple

from snippets import operative_text, operative_snippet, truncate_sentences, split_sentences

"""
Constitutional Statesman Engine
Evaluates Executive Orders strictly through the text, structure, and original principles 
of the United States Constitution (1787) and its Amendments (Bill of Rights, etc.)
from the perspective of an Early American Statesman (e.g., Madison, Hamilton, Jefferson).
"""

# Constitutional Dimension Lexicons with contextual weights
STATUTORY_FIDELITY_PATTERNS = [
    (r"\bpursuant to (the )?(act|statute|law|authority vested by congress)\b", 2.5),
    (r"\bfaithful(ly)? execut(e|ion|ing)\b", 3.0),
    (r"\bconsistent with (applicable )?law\b", 2.0),
    (r"\bauthorized by (the )?congress\b", 2.5),
    (r"\bto the extent permitted by law\b", 2.0),
    (r"\bsubject to the availability of appropriations\b", 2.0),
    (r"\bin accordance with (the )?constitution\b", 2.5),
    (r"\bprotect(ing)? (the )?(constitutional rights|civil liberties|free speech|due process)\b", 3.0),
    (r"\btransparency\b|\bpublic accountability\b|\bproper accounting\b", 1.5),
    (r"\bpeaceful\b|\btreaty obligations\b|\bdiplomatic\b", 1.5),
]

EXECUTIVE_OVERREACH_PATTERNS = [
    # Usurpation of Article I Legislative / Purse Powers
    (r"\bunilaterally (prohibit|levy|impose|mandate|suspend)\b", -3.5),
    (r"\bimpose (a )?(tariff|duty|tax|fee|impost) without\b", -4.0),
    (r"\bsuspend(ing)? (the )?(enforcement of|statute|law of congress|act of congress)\b", -4.0),
    (r"\breallocate funds? (without|notwithstanding) (congressional|appropriation)\b", -3.5),
    (r"\bsole executive discretion\b|\bplenary power\b", -2.5),
    (r"\bnotwithstanding any other provision of law\b", -2.0),
    (r"\bemergency powers? to bypass\b", -3.5),
    
    # Infringement of Bill of Rights (1st, 2nd, 4th, 5th, 6th)
    (r"\bwithout (a )?warrant\b|\bwarrantless\b", -4.0),
    (r"\bseiz(e|ure|ing) of private property\b|\bconfiscat(e|ion)\b", -3.5),
    (r"\bwithout due process\b|\bdetention without trial\b|\bhabeas corpus (be )?suspended\b", -4.5),
    (r"\bcensor(ship)?\b|\brestrict(ing)? (peaceable assembly|the press|religious exercise)\b", -4.0),
    (r"\bprohibit(ing)? (ownership|possession|bearing) of arms\b", -3.5),
    
    # Encroachment upon 10th Amendment Federalism / State Sovereignty
    (r"\bcommandeer(ing)? state (officials|governments|police)\b", -4.0),
    (r"\bcompel state legislatures\b|\bnullify state statutes\b", -3.5),
    (r"\bfederal control over (local|state) elections\b", -4.0),
    (r"\bsupplant state police powers\b", -3.5),
    
    # Domestic Military Prerogative
    (r"\bmartial law\b|\bmilitary commission to try civilians\b", -4.5),
    (r"\bdeploy(ing)? armed forces (against|within) domestic\b", -3.0),
]

def clean_directive_sentence(s: str) -> str:
    """Strips Federal Register publication artifacts, section headers, and formulaic preambles."""
    s = re.sub(r"\(\s*printed page \d+\s*\)", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\[Federal Register[^\]]+\]", "", s, flags=re.IGNORECASE)
    s = re.sub(r"^.*?by the authority vested in me[^:]*:\s*", "", s, flags=re.IGNORECASE)
    s = re.sub(r"^.*?\bit is hereby ordered:?\s*", "", s, flags=re.IGNORECASE)
    s = re.sub(r"^Section\s+\d+[\.\s]+(Purpose|Policy|General|Order)?[\.\s]*", "", s, flags=re.IGNORECASE)
    s = re.sub(r"^[\),;\.\s]+", "", s).strip()
    return s

def analyze_constitutional_sentiment(text: str, title: str = "") -> Dict[str, Any]:
    """
    Computes sentiment through the strict prism of the U.S. Constitution and its Framers.
    Returns compound score [-1.0, 1.0], valence, positive/negative/neutral breakdown, and tone tag.
    """
    combined_text = f"{title} {text}".lower()
    
    pos_score = 0.0
    neg_score = 0.0
    
    pos_matches = 0
    neg_matches = 0
    
    for pattern, weight in STATUTORY_FIDELITY_PATTERNS:
        matches = len(re.findall(pattern, combined_text))
        if matches > 0:
            pos_score += matches * weight
            pos_matches += matches

    for pattern, weight in EXECUTIVE_OVERREACH_PATTERNS:
        matches = len(re.findall(pattern, combined_text))
        if matches > 0:
            neg_score += matches * abs(weight)
            neg_matches += matches

    if "by the authority vested in me as president by the constitution and the laws" in combined_text:
        pos_score += 1.5
        pos_matches += 1

    if re.search(r"\bnational emergency\b|\bemergency declaration\b", combined_text):
        neg_score += 1.2
        neg_matches += 1

    total_signal = pos_score + neg_score
    if total_signal == 0:
        compound = 0.02
        val_pos = 0.1
        val_neg = 0.05
        val_neu = 0.85
    else:
        raw_diff = pos_score - neg_score
        compound = max(-1.0, min(1.0, raw_diff / (abs(raw_diff) + 5.0)))
        
        val_pos = round(pos_score / (total_signal + 2.0), 3)
        val_neg = round(neg_score / (total_signal + 2.0), 3)
        val_neu = round(max(0.0, 1.0 - (val_pos + val_neg)), 3)

    compound = round(compound, 2)

    if compound >= 0.08:
        valence = "Constitutional Fidelity"
    elif compound <= -0.08:
        valence = "Constitutional Friction / Overreach"
    else:
        valence = "Constitutional Neutral"

    tone_tag = determine_constitutional_tone_tag(combined_text, compound)

    return {
        "sentiment_compound": compound,
        "sentiment_valence": valence,
        "sentiment_pos": val_pos,
        "sentiment_neg": val_neg,
        "sentiment_neu": val_neu,
        "tone_tag": tone_tag
    }

def determine_constitutional_tone_tag(text_lower: str, compound: float) -> str:
    """Categorizes the primary Constitutional Article or Doctrine under scrutiny."""
    if re.search(r"\b(war|armed forces|military|commander in chief|army|navy|defense)\b", text_lower):
        if compound < -0.15:
            return "Art. II §2: Commander-in-Chief / War Prerogative Tension"
        return "Art. II §2: Commander-in-Chief Supervisory Authority"
    
    if re.search(r"\b(tariff|duty|customs|tax|revenue|appropriat|treasury)\b", text_lower):
        if compound < 0:
            return "Art. I §8: Legislative Prerogative Tension (Purse & Commerce)"
        return "Art. I §8: Delegated Tariff & Commerce Execution"
    
    if re.search(r"\b(search|seizure|warrant|property|takings|due process|compensation)\b", text_lower):
        if compound < 0:
            return "5th/14th Amend: Due Process & Property Rights Scrutiny"
        return "5th Amend: Regulatory Execution with Due Process"
        
    if re.search(r"\b(state|governors|police power|municipal|local government|federalism)\b", text_lower):
        if compound < 0:
            return "10th Amend: Federalism & State Sovereignty Tension"
        return "10th Amend: Intergovernmental Federalism Cooperation"
        
    if re.search(r"\b(foreign affairs|treaty|sanctions|ambassador|diplomatic|alien)\b", text_lower):
        return "Art. II §2: Diplomatic & Foreign Policy Prerogative"
        
    if re.search(r"\b(speech|press|religion|assembly|protest|civil liberties)\b", text_lower):
        return "1st Amend: Civil Liberties & Expressive Protections"

    if re.search(r"\b(civil service|personnel|holiday|seal|internal management|records)\b", text_lower):
        return "Art. II §3: Administrative Management & Civil Service"

    if compound >= 0.1:
        return "Art. II §3: Faithful Execution of Statutory Law"
    elif compound <= -0.1:
        return "Executive Prerogative & Inherent Power Assertion"
    else:
        return "Art. II §1: Executive Discretion & Internal Operations"

_SECTION_RE = re.compile(r"(?:^|\s)(?:Sec\.|Section|SECTION)\s*(\d+)\s*\.\s*([A-Z][A-Za-z ,;&'/-]{2,80}?)\s*\.\s+(?=[A-Z(\"\u201c])")
_ACTION_VERBS_RE = re.compile(
    r"\b(shall|hereby|directs?|ordered|establish(?:ed|es)?|prohibit(?:ed|s)?|amended|authoriz(?:ed|es)|"
    r"revoked|requires?|designated?|transferred|withdrawn|exempted|extended|delegated)\b",
    re.IGNORECASE,
)


def _directive_candidate(sentence: str, strict: bool = False) -> str:
    s_clean = clean_directive_sentence(sentence)
    s_clean = re.sub(r"^\((?:[a-z]|[ivx]+|\d+)\)\s*", "", s_clean)
    if len(s_clean) < 35 or len(s_clean) > 400:
        return ""
    if not _ACTION_VERBS_RE.search(s_clean):
        return ""
    if strict and not re.search(r"\b(shall|hereby|directs?)\b", s_clean, re.IGNORECASE):
        return ""
    if s_clean.lower().startswith(("general provisions", "by the authority", "by virtue of")) or s_clean.startswith("("):
        return ""
    return s_clean[0].upper() + s_clean[1:]


def extract_key_directives(text: str, title: str) -> List[Dict[str, str]]:
    """Extracts 2 to 4 actionable operative mandates from the text. Modern
    orders are split by their "Sec. N. Heading." structure so each directive
    gets its section heading as a title; older unsectioned orders fall back to
    the first action-bearing sentences of the operative text."""
    body = operative_text(text, title)
    directives = []
    seen = set()

    def add(title_text: str, description: str):
        norm = description[:45].lower()
        if description and norm not in seen:
            seen.add(norm)
            directives.append({"title": title_text, "description": description})

    sections = list(_SECTION_RE.finditer(" " + body))
    skip_headings = re.compile(r"general provisions|definitions|scope|severability|effective date", re.IGNORECASE)
    for i, m in enumerate(sections):
        heading = m.group(2).strip()
        if skip_headings.search(heading):
            continue
        section_end = sections[i + 1].start() if i + 1 < len(sections) else len(body) + 1
        section_text = (" " + body)[m.end():section_end]
        for sentence in split_sentences(section_text)[:4]:
            candidate = _directive_candidate(sentence)
            if candidate:
                add(heading, candidate)
                break
        if len(directives) >= 4:
            break

    if len(directives) < 2:
        # Sectioned orders open with purpose/findings prose, where incidental
        # verbs ("is transferred offshore") aren't directives; require an
        # operative verb there.
        for sentence in split_sentences(body):
            candidate = _directive_candidate(sentence, strict=bool(sections))
            if candidate:
                add(f"Directive {len(directives) + 1}", candidate)
            if len(directives) >= 4:
                break

    if not directives:
        directives.append({
            "title": "Operative Mandate",
            "description": truncate_sentences(body, 300) if body else
                f"Formal executive instruction issued by the President establishing official administrative policy on {title}."
        })

    return directives

def identify_affected_entities(text: str) -> List[str]:
    """Identifies the constitutional and societal entities governed or impacted."""
    entities = []
    t = text.lower()
    
    if re.search(r"\b(military|armed forces|army|navy|air force|defense|veterans|soldier|sailor)\b", t):
        entities.append("Armed Forces & Military Establishments")
    if re.search(r"\b(trade|tariff|importers?|exporters?|customs|foreign commerce|duties)\b", t):
        entities.append("Merchants, Importers & Commercial Enterprises")
    if re.search(r"\b(state|governors?|state legislatures?|municipalities|local authorities)\b", t):
        entities.append("Sovereign State Governments & Localities")
    if re.search(r"\b(civil service|federal employees|contractors|cabinet|officers|departments?)\b", t):
        entities.append("Executive Departments & Federal Civil Servants")
    if re.search(r"\b(citizens?|individual rights|private property|landowners?|public)\b", t):
        entities.append("Private Citizens & Property Owners")
    if re.search(r"\b(foreign|treaty|nations?|foreign states?|allies|diplomats?)\b", t):
        entities.append("Foreign Nations & International Entities")
    if re.search(r"\b(public health|hospitals|medical|welfare|relief)\b", t):
        entities.append("Public Health & Medical Institutions")
    if re.search(r"\b(banking|currency|gold|silver|treasury|revenue|bonds)\b", t):
        entities.append("Financial Institutions & Monetary Authorities")
        
    if not entities:
        entities = ["Executive Branch Departments", "General Body of the People"]
        
    return entities[:5]

_MONTHS = ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"]


def format_long_date(iso_date: str) -> str:
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", iso_date or "")
    if not m:
        return ""
    return f"{_MONTHS[int(m.group(2)) - 1]} {int(m.group(3))}, {m.group(1)}"


def generate_statesman_summary(
    title: str,
    president_name: str,
    signing_date: str,
    full_text: str,
    word_count: int,
    metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generates a full Constitutional Statesman breakdown:
    - Plain-English operational summary
    - Statesman's Constitutional Verdict (evaluating Article I, II, or Amendments)
    - Key operative directives
    - Impacted entities
    - Constitutional tone and sentiment
    """
    clean_title = re.sub(r"^Executive Order\s*(\d+(?:-[A-Z])?)?\s*[—–-]?\s*", "", title or "", flags=re.IGNORECASE).strip()

    # 1. Plain English Operative Action: who/when/what, then the order's own
    # first operative sentences (enacting clause and headings stripped), so the
    # summary says what this particular order does instead of generic filler.
    signed_on = format_long_date(signing_date)
    operative = operative_snippet(full_text, title, 420)
    operative_action = f"Signed by President {president_name}{f' on {signed_on}' if signed_on else ''}, "
    if clean_title:
        operative_action += f"this order concerns {clean_title.rstrip('.')}."
    else:
        operative_action += "this order reads:" if operative else "this order carries no recorded title or text."
    if operative:
        operative_action += f" {operative}"

    # 2. The Early Statesman's Constitutional Verdict
    tone_tag = metrics["tone_tag"]
    compound = metrics["sentiment_compound"]
    
    if "Faithful Execution" in tone_tag:
        verdict = (
            f"Constitutional Assessment: An early statesman would view this measure favorably under Article II, Section 3 "
            f"(the Take Care Clause). The President operates strictly within the ambit of executing established laws and "
            f"supervising departmental subordinates, respecting the supremacy of the legislative branch without fabricating "
            f"novel statutory obligations."
        )
    elif "Legislative Prerogative" in tone_tag:
        verdict = (
            f"Constitutional Assessment: An early statesman would subject this decree to rigorous scrutiny under Article I, Section 8. "
            f"The Framers deliberately committed commerce, taxation, tariffs, and revenue to Congress alone. To the extent this order "
            f"imposes duties or financial burdens without explicit statutory pre-authorization, it creates friction with the separation of powers."
        )
    elif "Commander-in-Chief" in tone_tag:
        verdict = (
            f"Constitutional Assessment: Scrutinized through Article II, Section 2, this action exercises the President's constitutional role "
            f"as Commander in Chief. Early Framers recognized broad executive discretion in commanding military forces during conflict, "
            f"provided it remains bounded by congressional declarations and respects civilian domestic courts."
        )
    elif "Due Process" in tone_tag:
        verdict = (
            f"Constitutional Assessment: Evaluated against the Fifth Amendment, this action touches upon property or economic rights. "
            f"An early statesman would insist upon strict adherence to due process of law and the constitutional guarantee that private "
            f"holdings shall not be encumbered or taken for public purposes without just compensation and lawful process."
        )
    elif "Federalism" in tone_tag:
        verdict = (
            f"Constitutional Assessment: Reviewed under the Tenth Amendment and the principle of dual federalism, this order touches upon "
            f"domains traditionally reserved to the sovereign States. The Framers would caution against any attempt to commandeer state "
            f"officers or displace local police powers through federal executive fiat."
        )
    elif "Foreign Affairs" in tone_tag:
        verdict = (
            f"Constitutional Assessment: In the arena of foreign relations and national defense, the Framers recognized the executive "
            f"as the primary organ of communication and diplomacy (Article II, Section 2), provided formal treaties receive the advice "
            f"and consent of the Senate."
        )
    else:
        if compound >= 0:
            verdict = (
                f"Constitutional Assessment: This action represents an orderly exercise of Article II administrative discretion, "
                f"managing the internal machinery and personnel of the executive branch without abridging the ancient liberties of the people."
            )
        else:
            verdict = (
                f"Constitutional Assessment: An early statesman would regard this order with wariness, cautioning that energetic executive "
                f"discretion must never eclipse the enumerated boundaries established by the representatives of the people in Congress."
            )

    full_summary = f"{operative_action}\n\n{verdict}"
    directives = extract_key_directives(full_text, clean_title)
    affected = identify_affected_entities(full_text)

    return {
        "summary_plain_english": full_summary,
        "key_directives": directives,
        "who_it_affects": affected,
        "tone_tag": tone_tag
    }
