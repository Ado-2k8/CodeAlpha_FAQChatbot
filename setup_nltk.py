"""Télécharge les ressources NLTK nécessaires. À exécuter une seule fois après pip install."""
import nltk

for pkg in ["punkt", "punkt_tab", "stopwords", "wordnet"]:
    nltk.download(pkg)

print("Ressources NLTK téléchargées avec succès.")
