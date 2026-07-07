# CodeAlpha_FAQChatbot

Chatbot de réponse aux questions fréquentes (FAQ), réalisé dans le cadre du stage
Artificial Intelligence chez **CodeAlpha** (Task 2).

## 🎯 Fonctionnement

1. Une base de FAQ (questions/réponses) est chargée depuis `data/faqs.json`.
2. Chaque question est prétraitée avec **NLTK** : nettoyage du texte, tokenisation,
   suppression des mots vides (stopwords), lemmatisation.
3. Les questions sont vectorisées avec un **TF-IDF hybride** :
   - un vectoriseur au niveau des mots (unigrammes + bigrammes),
   - un vectoriseur au niveau des n-grammes de caractères (3 à 5),
   pour être plus robuste face aux variations morphologiques (ex: *pay* / *payment*).
4. La question de l'utilisateur est comparée à toutes les questions de la FAQ via la
   **similarité cosinus** (moyenne des deux similarités ci-dessus).
5. La réponse associée à la question la plus proche est renvoyée, si le score dépasse
   un seuil de confiance (sinon un message de repli est affiché).

## 📁 Structure du projet

```
CodeAlpha_FAQChatbot/
├── app.py              # Interface utilisateur Streamlit (chat)
├── chatbot.py          # Moteur du chatbot (TF-IDF + cosine similarity) + mode CLI
├── preprocessing.py     # Pipeline NLP (NLTK)
├── setup_nltk.py        # Script pour télécharger les ressources NLTK
├── data/
│   └── faqs.json        # Base de connaissances (30 questions/réponses e-commerce)
├── requirements.txt
└── README.md
```

## 🚀 Installation

```bash
git clone https://github.com/<votre-user>/CodeAlpha_FAQChatbot.git
cd CodeAlpha_FAQChatbot
pip install -r requirements.txt
python setup_nltk.py
```

## ▶️ Utilisation

### Interface web (Streamlit)
```bash
streamlit run app.py
```
Puis ouvrez le lien affiché (par défaut http://localhost:8501).

### Mode ligne de commande
```bash
python chatbot.py
```

## 🧪 Exemple

```
Vous: How do I cancel my order?
Bot (0.72): You can cancel your order within 1 hour of placing it by contacting
            our support team or from your order history page.
```

## 🛠️ Stack technique

- Python 3
- NLTK (préprocessing NLP)
- scikit-learn (TF-IDF, cosine similarity)
- Streamlit (interface utilisateur)

## 📌 Limites connues

Le matching est purement lexical (TF-IDF). Il ne comprend pas les synonymes
totalement différents (ex: "money back" vs "refund policy" sans mot commun).
Une amélioration possible serait d'utiliser des embeddings sémantiques
(ex: `sentence-transformers`) pour un matching basé sur le sens plutôt que
sur les mots exacts.

## 👤 Auteur

Projet réalisé dans le cadre du stage AI Internship — CodeAlpha (2026).
