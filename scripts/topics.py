import re

"""
Controlled Topic/Category Taxonomy

A fixed, deterministic keyword-scored classifier — mirrors the pattern-matching
approach already used in constitutional_engine.py (no LLM call in this pipeline).
Distinct from tone_tag (constitutional/doctrinal framing) and who_it_affects
(impacted entities): this is a plain-language policy-area taxonomy meant for
browsing/filtering ("Immigration", "Trade", ...).
"""

TOPIC_PATTERNS: dict[str, list[str]] = {
    "Immigration & Border Security": [
        r"\bimmigra(nt|tion|nts)\b", r"\bborder security\b", r"\basylum\b", r"\bvisas?\b",
        r"\brefugees?\b", r"\bdeportation\b", r"\bnaturalization\b", r"\bundocumented\b",
        r"\bcustoms and border protection\b", r"\balien(s)?\b",
    ],
    "National Security & Defense": [
        r"\bnational security\b", r"\barmed forces\b", r"\bmilitary\b", r"\bdefense department\b",
        r"\bpentagon\b", r"\bveterans?\b", r"\b(the )?navy\b", r"\b(the )?army\b", r"\bair force\b",
        r"\bhomeland security\b", r"\bterroris(m|t|ts)\b", r"\bcommander in chief\b",
    ],
    "Trade & Tariffs": [
        r"\btariffs?\b", r"\bimports?\b", r"\bexports?\b", r"\bcustoms duties\b",
        r"\btrade agreements?\b", r"\bforeign commerce\b", r"\bdumping\b", r"\bquotas?\b",
    ],
    "Energy & Environment": [
        r"\benergy\b", r"\bclimate\b", r"\bemissions?\b", r"\brenewable\b", r"\bpetroleum\b",
        r"\bnatural gas\b", r"\bcoal\b", r"\bpollution\b", r"\benvironmental protection\b",
        r"\bconservation\b", r"\bclean (air|water)\b", r"\bwildlife\b",
    ],
    "Healthcare & Public Health": [
        r"\bhealth\s?care\b", r"\bpublic health\b", r"\bmedicaid\b", r"\bmedicare\b",
        r"\bvaccin(e|es|ation)\b", r"\bpandemic\b", r"\bhospitals?\b", r"\bdisease\b",
        r"\bepidemic\b", r"\bopioid\b",
    ],
    "Labor & Employment": [
        r"\blabor\b", r"\bemployment\b", r"\bworkers?\b", r"\bwages?\b", r"\bunions?\b",
        r"\boccupational safety\b", r"\bcollective bargaining\b", r"\bminimum wage\b",
        r"\bworkforce\b", r"\bunemployment\b",
    ],
    "Education": [
        r"\beducation\b", r"\bschools?\b", r"\bstudents?\b", r"\bstudent loans?\b",
        r"\buniversit(y|ies)\b", r"\bcolleges?\b",
    ],
    "Technology & Cybersecurity": [
        r"\bcybersecurity\b", r"\bartificial intelligence\b", r"\btechnology\b",
        r"\bdata privacy\b", r"\bdigital\b", r"\bcyberspace\b", r"\bcyber\b", r"\bcomputer\b",
    ],
    "Civil Rights & Liberties": [
        r"\bcivil rights\b", r"\bdiscrimination\b", r"\bequal (protection|opportunity)\b",
        r"\bfreedom of (speech|religion|the press)\b", r"\bvoting rights\b",
        r"\bdisabilit(y|ies)\b", r"\bcivil liberties\b",
    ],
    "Criminal Justice & Law Enforcement": [
        r"\bcriminal justice\b", r"\blaw enforcement\b", r"\bpolice\b", r"\bprisons?\b",
        r"\bsentencing\b", r"\bcrime\b", r"\bjustice department\b", r"\bfederal bureau of investigation\b",
    ],
    "Foreign Policy & Diplomacy": [
        r"\bforeign (policy|affairs|nations?|states?)\b", r"\bdiplomat(ic|s)?\b",
        r"\btreat(y|ies)\b", r"\bsanctions?\b", r"\bambassadors?\b", r"\bembargo\b",
        r"\bunited nations\b", r"\bstate department\b",
    ],
    "Economy & Finance": [
        r"\beconom(y|ic|ics)\b", r"\bbanking\b", r"\bfinancial\b", r"\btreasury\b",
        r"\bcurrency\b", r"\binflation\b", r"\bfederal reserve\b", r"\bbudget\b", r"\bsecurities\b",
    ],
    "Agriculture": [
        r"\bagricultur(e|al)\b", r"\bfarm(s|ers|ing)?\b", r"\bcrops?\b", r"\blivestock\b",
        r"\brural\b",
    ],
    "Government Operations & Civil Service": [
        r"\bcivil service\b", r"\bfederal employees?\b", r"\bexecutive departments?\b",
        r"\breorganization\b", r"\bfederal workforce\b", r"\badministrative procedure\b",
        r"\bregulatory reform\b",
    ],
    "Infrastructure & Transportation": [
        r"\binfrastructure\b", r"\btransportation\b", r"\bhighways?\b", r"\brailroads?\b",
        r"\baviation\b", r"\bports?\b", r"\bbridges?\b",
    ],
    "Housing": [
        r"\bhousing\b", r"\bmortgages?\b", r"\bhomeowners?\b", r"\baffordable housing\b",
        r"\burban development\b",
    ],
}

TOPIC_NAMES = sorted(TOPIC_PATTERNS.keys())

# Kept distinct from "Government Operations & Civil Service" so that filter
# stays a genuine keyword-matched category rather than absorbing every order
# whose sparse/historical text didn't hit any topic's keywords at all
# (~25% of the corpus, mostly short 18th-20th century administrative decrees).
UNCATEGORIZED_TOPIC = "Uncategorized"

ALL_TOPIC_NAMES = TOPIC_NAMES + [UNCATEGORIZED_TOPIC]


def classify_topics(text: str, max_topics: int = 3, min_score: int = 2) -> list[str]:
    """Scores text against each topic's keyword set and returns the top matches.

    A topic only qualifies at min_score+ keyword hits to avoid tagging an order
    off a single incidental word; if nothing clears that bar, the single
    highest-scoring topic (score >= 1) is used instead. Orders with no keyword
    hits at all fall back to UNCATEGORIZED_TOPIC rather than a real topic.
    """
    t = (text or "").lower()
    scores: list[tuple[str, int]] = []
    for topic, patterns in TOPIC_PATTERNS.items():
        score = sum(len(re.findall(p, t)) for p in patterns)
        if score > 0:
            scores.append((topic, score))

    scores.sort(key=lambda x: -x[1])

    qualified = [name for name, score in scores if score >= min_score]
    if qualified:
        return qualified[:max_topics]
    if scores:
        return [scores[0][0]]
    return [UNCATEGORIZED_TOPIC]
