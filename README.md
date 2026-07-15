# CodeAlpha_FAQChatbot

FAQ chatbot built as part of the **CodeAlpha** Artificial Intelligence internship (Task 2).

## How it works

1. A FAQ knowledge base (questions/answers) is loaded from `data/faqs.json`.
2. Each question is preprocessed with **NLTK**: text cleaning, tokenization,
   stopword removal, lemmatization.
3. Questions are vectorized using a **hybrid TF-IDF** approach:
   - a word-level vectorizer (unigrams + bigrams),
   - a character n-gram vectorizer (3 to 5 characters),
   to be more robust to morphological variations (e.g. *pay* / *payment*).
4. The user's question is compared to all FAQ questions using **cosine similarity**
   (average of both similarities above).
5. The answer linked to the closest question is returned, if the score is above
   a confidence threshold (otherwise a fallback message is shown).

## Project structure

```
CodeAlpha_FAQChatbot/
├── app.py              # Streamlit chat UI
├── chatbot.py          # Chatbot engine (TF-IDF + cosine similarity) + CLI mode
├── preprocessing.py     # NLP pipeline (NLTK)
├── setup_nltk.py        # Script to download required NLTK resources
├── data/
│   └── faqs.json        # Knowledge base (30 e-commerce Q&A pairs)
├── requirements.txt
└── README.md
```

## Installation

```bash
git clone https://github.com/Ado-2k8/CodeAlpha_FAQChatbot.git
cd CodeAlpha_FAQChatbot
pip install -r requirements.txt
python setup_nltk.py
```

## Usage

### Web interface (Streamlit)
```bash
streamlit run app.py
```
Then open the link shown in the terminal (default: http://localhost:8501).

### Command-line mode
```bash
python chatbot.py
```

## Example

```
You: How do I cancel my order?
Bot (1.00): You can cancel your order within 1 hour of placing it by contacting
            our support team or from your order history page.
```

## Tech stack

- Python 3
- NLTK (NLP preprocessing)
- scikit-learn (TF-IDF, cosine similarity)
- Streamlit (user interface)

## Known limitations

Matching is purely lexical (TF-IDF). It doesn't understand fully different
synonyms with no shared words (e.g. "money back" vs "refund policy").
A possible improvement would be to use semantic embeddings
(e.g. `sentence-transformers`) for meaning-based matching instead of
exact-word matching.

## Author

Project built as part of the AI Internship — CodeAlpha (2026).
