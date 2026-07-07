"""
NLP preprocessing module for the FAQ chatbot.
Uses NLTK for: tokenization, stopword removal, lemmatization.
"""
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Make sure NLTK resources are available (silent if already present)
for pkg in ["punkt", "punkt_tab", "stopwords", "wordnet"]:
    try:
        nltk.data.find(pkg)
    except LookupError:
        nltk.download(pkg, quiet=True)

_lemmatizer = WordNetLemmatizer()
_stop_words = set(stopwords.words("english"))


def clean_text(text: str) -> str:
    """Cleans the text: lowercase + removes punctuation/stray digits."""
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def preprocess(text: str) -> str:
    """
    Full NLP preprocessing pipeline:
    cleaning -> tokenization -> stopword removal -> lemmatization.
    Returns a string of lemmatized tokens, ready for vectorization.
    """
    cleaned = clean_text(text)
    tokens = word_tokenize(cleaned)
    tokens = [
        _lemmatizer.lemmatize(tok)
        for tok in tokens
        if tok not in _stop_words and len(tok) > 1
    ]
    return " ".join(tokens)
