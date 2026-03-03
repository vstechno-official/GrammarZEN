import re
import nltk
from textblob import TextBlob

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger', quiet=True)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)


def analyze_sentiment(text: str):
    blob = TextBlob(text)
    polarity = round(blob.sentiment.polarity, 2)
    if polarity > 0.1:
        sentiment = 'positive'
    elif polarity < -0.1:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
    return sentiment, polarity


def calculate_readability(text: str) -> float:
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    words = text.split()
    if not sentences or not words:
        return 0.0
    syllables = sum(_count_syllables(w) for w in words)
    asl = len(words) / len(sentences)
    asw = syllables / len(words)
    score = 206.835 - (1.015 * asl) - (84.6 * asw)
    return round(max(0.0, min(100.0, score)), 1)


def _count_syllables(word: str) -> int:
    word = word.lower().strip(".,!?;:")
    if not word:
        return 1
    vowels = 'aeiouy'
    count = 0
    prev_vowel = False
    for ch in word:
        is_v = ch in vowels
        if is_v and not prev_vowel:
            count += 1
        prev_vowel = is_v
    if word.endswith('e') and count > 1:
        count -= 1
    return max(1, count)


def generate_suggestions(text: str, issues) -> list:
    suggestions = []
    words = text.split()
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    if not sentences:
        return suggestions
    avg_len = len(words) / len(sentences)
    if avg_len > 30:
        suggestions.append("Consider breaking long sentences into shorter ones for clarity.")
    if avg_len < 5 and len(sentences) > 2:
        suggestions.append("Your sentences seem very short. Consider combining some for better flow.")
    unique = set(w.lower().strip('.,!?;:') for w in words)
    ratio = len(unique) / max(len(words), 1)
    if ratio < 0.4:
        suggestions.append("Try varying your vocabulary to make the text more engaging.")
    passive_pattern = re.compile(r'\b(is|are|was|were|be|been|being)\s+\w+ed\b', re.IGNORECASE)
    if len(passive_pattern.findall(text)) > 2:
        suggestions.append("You have multiple passive voice constructions. Consider using active voice.")
    filler_words = ['very', 'really', 'quite', 'basically', 'literally', 'actually', 'just']
    found_fillers = [w for w in filler_words if re.search(r'\b' + w + r'\b', text, re.IGNORECASE)]
    if found_fillers:
        suggestions.append(f"Consider removing filler words: {', '.join(found_fillers)}.")
    error_count = sum(1 for i in issues if i.severity == 'error')
    if error_count > 5:
        suggestions.append("Multiple grammar errors detected. Review subject-verb agreement and tense consistency.")
    return suggestions[:5]
