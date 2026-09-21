import re
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import textstat

_analyzer = SentimentIntensityAnalyzer()

def clean_text_from_html(html_content: str) -> str:
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    # Remove script, style, and navigation tags
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    text = soup.get_text(separator=" ")
    # Collapse multiple whitespaces and newlines
    text = re.sub(r"\s+", " ", text).strip()
    return text

def compute_metrics(text: str) -> dict:
    if not text or len(text.strip()) == 0:
        return {
            "word_count": 0,
            "char_count": 0,
            "reading_time_minutes": 0,
            "flesch_kincaid_grade": 0.0,
            "sentiment_compound": 0.0,
            "sentiment_pos": 0.0,
            "sentiment_neg": 0.0,
            "sentiment_neu": 1.0,
            "sentiment_valence": "Neutral"
        }

    # Length metrics
    words = text.split()
    word_count = len(words)
    char_count = len(text)
    reading_time_minutes = max(1, round(word_count / 200)) if word_count > 0 else 0

    # Readability (Flesch-Kincaid)
    try:
        # Evaluate on the first 10,000 characters for speed and consistency
        sample_for_readability = text[:10000]
        grade_level = round(textstat.flesch_kincaid_grade(sample_for_readability), 1)
    except Exception:
        grade_level = 12.0

    # Sentiment analysis (VADER)
    # Executive orders can be lengthy; evaluate the introductory operative mandate
    sample_for_sentiment = text[:8000]
    scores = _analyzer.polarity_scores(sample_for_sentiment)
    compound = scores["compound"]
    
    if compound >= 0.05:
        valence = "Positive"
    elif compound <= -0.05:
        valence = "Urgent/Negative"
    else:
        valence = "Neutral"

    return {
        "word_count": word_count,
        "char_count": char_count,
        "reading_time_minutes": reading_time_minutes,
        "flesch_kincaid_grade": grade_level,
        "sentiment_compound": compound,
        "sentiment_pos": scores["pos"],
        "sentiment_neg": scores["neg"],
        "sentiment_neu": scores["neu"],
        "sentiment_valence": valence
    }

if __name__ == "__main__":
    sample = "By the authority vested in me as President, I hereby order immediate action to protect public health and restore vital infrastructure across all departments."
    res = compute_metrics(sample)
    print("Sample metrics test:")
    for k, v in res.items():
        print(f"  {k}: {v}")
