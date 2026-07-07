"""
Module de préprocessing NLP pour le chatbot FAQ.
Utilise NLTK pour : tokenisation, suppression des stopwords, lemmatisation.
"""
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# S'assure que les ressources NLTK sont disponibles (silencieux si déjà présentes)
for pkg in ["punkt", "punkt_tab", "stopwords", "wordnet"]:
    try:
        nltk.data.find(pkg)
    except LookupError:
        nltk.download(pkg, quiet=True)

_lemmatizer = WordNetLemmatizer()
_stop_words = set(stopwords.words("english"))


def clean_text(text: str) -> str:
    """Nettoie le texte : minuscules + suppression de la ponctuation/chiffres isolés."""
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def preprocess(text: str) -> str:
    """
    Pipeline complète de préprocessing NLP :
    nettoyage -> tokenisation -> suppression stopwords -> lemmatisation.
    Retourne une chaîne de tokens lemmatisés, prête pour la vectorisation.
    """
    cleaned = clean_text(text)
    tokens = word_tokenize(cleaned)
    tokens = [
        _lemmatizer.lemmatize(tok)
        for tok in tokens
        if tok not in _stop_words and len(tok) > 1
    ]
    return " ".join(tokens)
